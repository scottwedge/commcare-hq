$(function () {
    ko.applyBindings(new XFormListViewModel(), $("#history")[0]);
});

function pad_zero(val) {
    if (val < 10) {
        return "0" + val;
    } else {
        return val;
    }
}

function format_date(isodatestring) {
    if (isodatestring == "" || isodatestring == null) {
        return 'present';
    }
    //parse nad format the date timestamps - seconds since epoch into date object
    var date = new Date(isodatestring.split('+')[0]);

    // Get the TZ offset based the project's timezone and create a new date
    // object with that as it's "UTC" date
    var _configuredTZOffset = CASE_DETAILS.timezone_offset;
    date = new Date(date.getTime() + _configuredTZOffset);

    // hours part from the timestamp
    var hours = pad_zero(date.getUTCHours());
    // minutes part from the timestamp
    var minutes = pad_zero(date.getUTCMinutes());

    // seconds part from the timestamp
    var seconds = pad_zero(date.getUTCSeconds());

    var year = date.getUTCFullYear();
    var month = date.getUTCMonth() + 1;
    var day = date.getUTCDate();

    //return  year + '/' + month + '/' + day + ' ' + hours + ':' + minutes + ':' + second_str;
    //return  year + '/' + month + '/' + day;
    return  year + '-' + month + '-' + day + ' ' + hours + ":" + minutes;

}

function format_user(username) {
    if (username === undefined || username === null) {
        return "Unknown";
    }
    else {
        return username.split('@')[0];
    }
}

function XFormDataModel(data) {
    var self = this;
    self.id = ko.observable(data['_id']);
    self.case_id = ko.observable(data.case_id); //helper populated
    self.xmlns = ko.observable(data.xmlns);
    self.domain = ko.observable(data.domain);
    self.app_id = ko.observable(data.app_id);
    self.received_on = ko.observable(format_date(data.received_on));

    if (typeof data.form.meta !== 'undefined') {
        self.timeStart = ko.observable(format_date(data.form.meta.timeStart));
        self.timeEnd = ko.observable(format_date(data.form.meta.timeEnd));
        self.userID = ko.observable(data.form.meta.userID);
        self.username = ko.observable(format_user(data.form.meta.username));
        self.deviceID = ko.observable(data.form.meta.deviceID);
    } else {
        self.timeStart = ko.observable(null);
        self.timeEnd = ko.observable(null);
        self.userID = ko.observable(null);
        self.username = ko.observable(format_user(null));
        self.deviceID = ko.observable(null);
    }

    self.form_type = ko.observable(data.form['#type']);
    self.form_data = ko.observable(data.form);
    self.readable_name = ko.observable(data.es_readable_name);
};

function FormTypeFacetModel(data) {
    var self = this;
    //{"form_type_facets": {"_type": "terms", "total": 854, "terms": [{"count": 605, "term": "dots_form"}, {"count": 168, "term": "data"}, {"count": 75, "term": "progress_note"}, {"count": 6, "term": "bloodwork"}], "other": 0, "missing": 0},
    self.form_name = ko.observable(data.term);
    self.form_count = ko.observable(data.count);
};

function FormDateHistogram(data) {
    var self = this;
    self.es_time = ko.observable(data.time);
    self.form_count = ko.observable(data.count);
};

function XFormListViewModel() {
    var self = this;

    self.pagination_options = [10,25,50,100];

    self.xforms = ko.observableArray([]);
    self.page_size = ko.observable(10);
    self.disp_page_index = ko.observable(1);
    self.total_rows = ko.observable(0);
    self.page_count = ko.observable(0);
    self.selected_xform_idx = ko.observable(-1);
    self.selected_xform_doc_id = ko.observable("");
    self.selected_xforms = ko.observableArray([]);

    self.form_type_facets = ko.observableArray([]);
    self.form_recv_facets = ko.observableArray([]);

    self.data_loading = ko.observable(false);

    var api_url = CASE_DETAILS.xform_api_url;

    self.xform_id_query = function () {
        //hacky query based upon xform_ids due to nested case properties not being indexed in pillowtop at the moment

        var start_num = self.disp_page_index() || 1;
        var start_range = (start_num - 1) * self.page_size();
        var end_range = start_range + self.page_size();
        var xform_ids = CASE_DETAILS.xform_ids;

        if (end_range > xform_ids.length) {
            end_range = xform_ids.length;
        }
        xform_ids.reverse();

        return {
            "filter": {
                "ids": {
                    "values": _.map(_.range(start_range, end_range),
                                    function(idx) {
                                        return xform_ids[idx];
                                    })
                }
            },
            "from": 0,
            "size": self.page_size(),
            "sort": [{"received_on": "desc"}]
        };
    };


    self.get_xform_data = function(xform_id) {
        //method for getting individual xform via GET
        $.cachedAjax({
            "type": "GET",
            "url": CASE_DETAILS.xform_ajax_url + xform_id + "/",
            "success": function(data) {
                $("#xform_data_panel").html(data);
                //$("#xform_data_panel").html('<h2>selected ' + xform_id + "</h2>");
            },
            "error": function(data) {
                console.log("get xform error");
                console.log(data);
            },
            "complete": function(data) {
            }
        })
    };

    self.run_es_query = function(query, success_cb) {
        //generic caller for ES query
        self.data_loading(true);
        $.ajax({
            "type": "POST",
            "url":  api_url,
            "data": ko.toJSON(query),
            "success": function(data) {
                success_cb(data);
            }, //end success
            "error": function(data) {
                console.log("Error");
                console.log(data);
            },
            "complete": function(data){
                //{#                        self.is_loading(false);#}
                self.data_loading(false);
            }
        });
    };

    self.xform_history_cb = function(data) {
        //callback for rendering the xforms list
        //todo until indexing is fixed for nested case blocks
        //self.total_rows(data['hits']['total']);
        self.total_rows(CASE_DETAILS.xform_ids.length);
        self.calc_page_count();
        var mapped_xforms = $.map(data['hits']['hits'], function (item) {
            return new XFormDataModel(item['_source']);
        });
        self.xforms(mapped_xforms);
        self.selected_xform_idx(-1);
    };

    self.refresh_forms = function () {
        self.run_es_query(self.xform_id_query(), self.xform_history_cb);
    };

    self.calc_page_count = function() {
        self.page_count(Math.ceil(self.total_rows()/self.page_size()));
    };

    //main function data collection - entry point if you will
    self.refresh_forms();

    self.nextPage = function() {
        self.disp_page_index(self.disp_page_index() + 1);
        self.refresh_forms();
    };

    self.prevPage = function() {
        self.disp_page_index(self.disp_page_index() - 1);
        self.refresh_forms();
    };

    self.clickRow = function(item) {
        $("#xform_data_panel").html("<img src='/static/hqwebapp/img/ajax-loader.gif' alt='loading indicator' />");
        var idx = self.xforms().indexOf(item);

        self.get_xform_data(self.xforms()[idx].id());
        self.selected_xform_idx(idx);
        self.selected_xform_doc_id(self.xforms()[idx].id());
        if (idx > -1) {
            self.selected_xforms([]);
            self.selected_xforms.push(self.xforms()[self.selected_xform_idx()]);
        }
    };

    self.page_start_num = ko.computed(function() {
        var start_num = self.disp_page_index() || 1;
        var calc_start_num = ((start_num - 1) * self.page_size()) + 1;
        return calc_start_num;
    });

    self.page_end_num = ko.computed(function() {
        var start_num = self.disp_page_index() || 1;
        var end_page_num = ((start_num - 1) * self.page_size()) + self.page_size();
        if (end_page_num > self.total_rows()) {
            return self.total_rows();
        }
        else {
            return end_page_num;
        }
    });


    self.page_size_changed = self.page_size.subscribe(function () {
        var disp_index = self.disp_page_index();
        self.calc_page_count();
        if (disp_index > self.page_count()) {
            self.disp_page_index(self.page_count());
        } else {
            self.refresh_forms();
        }
    });

    self.disp_page_index_changed = self.disp_page_index.subscribe(function () {
        self.refresh_forms();
    });

    self.all_pages = function() {
        return _.range(1, self.page_count()+1);
    };

    self.xform_view = ko.computed(function () {
        return self.selected_xform_doc_id() !== undefined;
    });

    self.row_highlight = ko.computed(function() {
        //hitting next page will not disappear the xform display just remove the highlight
        if (self.selected_xform_idx() === -1) {
            return false;
        } else  {
            if (self.selected_xforms[0] !== undefined) {
                return self.selected_xform_doc_id() === self.selected_xforms()[0].id();
            } else {
                return true;
            }
        }
    });
};

