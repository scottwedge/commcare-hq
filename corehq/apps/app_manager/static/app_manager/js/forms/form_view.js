/* globals SyntaxHighlighter */
hqDefine("app_manager/js/forms/form_view", function() {
    var initialPageData = hqImport("hqwebapp/js/initial_page_data").get,
        appManagerUtils = hqImport('app_manager/js/app_manager');
    appManagerUtils.setPrependedPageTitle("\u2699 ", true);
    appManagerUtils.setAppendedPageTitle(gettext("Form Settings"));
    appManagerUtils.updatePageTitle(initialPageData("form_name"));

    function formFilterMatches(filter, patternMatches, substringMatches) {
        if (typeof(filter) !== 'string') {
            return false;
        }

        var result = false;
        $.each(patternMatches, function(index, pattern) {
            result = result || filter.match(pattern);
        });

        $.each(substringMatches, function(index, sub) {
            result = result || filter.indexOf(sub) !== -1;
        });

        return result;
    }

    function formFilterModel() {
        var self = {};
        var patterns = initialPageData('form_filter_patterns');

        self.formFilter = ko.observable(initialPageData('form_filter'));

        self.caseReferenceNotAllowed = ko.computed(function() {
            var moduleUsesCase = initialPageData('all_other_forms_require_a_case') && initialPageData('form_requires') === 'case';
            if (!moduleUsesCase || (initialPageData('put_in_root') && !initialPageData('root_requires_same_case'))) {
                // We want to determine here if the filter expression references
                // any case but the user case.
                var filter = self.formFilter();
                if (typeof(filter) !== 'string') {
                    return true;
                }

                $.each(patterns.usercase_substring, function(index, sub) {
                    filter = filter.replace(sub, '');
                });

                if (formFilterMatches(filter, patterns.case, patterns.case_substring)) {
                    return true;
                }
            }
            return false;
        });

        self.userCaseReferenceNotAllowed = ko.computed(function() {
            return !initialPageData('is_usercase_in_use') && formFilterMatches(
                self.formFilter(), patterns.usercase, patterns.usercase_substring
            );
        });

        self.allowed = ko.computed(function () {
            return !self.formFilter() || !self.caseReferenceNotAllowed() && !self.userCaseReferenceNotAllowed();
        });

        return self;
    }

    $(function (){
        // Validation for build
        var setupValidation = hqImport('app_manager/js/app_manager').setupValidation;
        setupValidation(hqImport("hqwebapp/js/initial_page_data").reverse("validate_form_for_build"));

        // Analytics for renaming form
        $(".appmanager-edit-title").on('click', '.btn-success', function() {
            hqImport('analytix/js/kissmetrix').track.event("Renamed form from form settings page");
        });

        // Settings > Logic
        var $formFilter = $('#form-filter');
        if ($formFilter.length && initialPageData('allow_form_filtering')) {
            $('#form-filter').koApplyBindings(formFilterModel());
        }

        if (initialPageData('allow_form_workflow')) {
            var FormWorkflow = hqImport('app_manager/js/forms/form_workflow').FormWorkflow;
            var labels = {};
            labels[FormWorkflow.Values.DEFAULT] = gettext("Home Screen");
            labels[FormWorkflow.Values.ROOT] = gettext("First Menu");
            labels[FormWorkflow.Values.MODULE] = gettext("Menu: ") + initialPageData('module_name');
            if (initialPageData('root_module_name')) {
                labels[FormWorkflow.Values.PARENT_MODULE] = gettext("Parent Menu: ") + initialPageData('root_module_name');
            }
            labels[FormWorkflow.Values.PREVIOUS_SCREEN] = gettext("Previous Screen");

            var options = {
                labels: labels,
                workflow: initialPageData('post_form_workflow'),
                workflow_fallback: initialPageData('post_form_workflow_fallback'),
            };

            if (hqImport('hqwebapp/js/toggles').toggleEnabled('FORM_LINK_WORKFLOW') || initialPageData('uses_form_workflow')) {
                labels[FormWorkflow.Values.FORM] = gettext("Link to other form");
                options.forms = initialPageData('linkable_forms');
                options.formLinks = initialPageData('form_links');
                options.formDatumsUrl = hqImport('hqwebapp/js/initial_page_data').reverse('get_form_datums');
            }

            $('#form-workflow').koApplyBindings(new FormWorkflow(options));
        }

        // Settings > Advanced
        $('#auto-gps-capture').koApplyBindings({
            auto_gps_capture: ko.observable(initialPageData('auto_gps_capture')),
        });

        if (initialPageData('is_training_module')) {
            $('#release-notes-setting').koApplyBindings({
                is_release_notes_form: ko.observable(initialPageData('is_release_notes_form')),
                enable_release_notes: ko.observable(initialPageData('enable_release_notes')),
                is_allowed_to_be_release_notes_form: ko.observable(initialPageData('is_allowed_to_be_release_notes_form')),
                toggle_enable: function() {
                    var allowed = this.is_release_notes_form();
                    if (!allowed){
                        this.enable_release_notes(false);
                    }
                    return true;
                },
            });
        }

        var $shadowParent = $('#shadow-parent');
        if ($shadowParent.length) {
            $shadowParent.koApplyBindings({
                shadow_parent: ko.observable(initialPageData('shadow_parent_form_id')),
            });
        } else if (hqImport('hqwebapp/js/toggles').toggleEnabled('NO_VELLUM')) {
            $('#no-vellum').koApplyBindings({
                no_vellum: ko.observable(initialPageData('no_vellum')),
            });
        }

        if (hqImport('hqwebapp/js/toggles').toggleEnabled('CUSTOM_INSTANCES')) {
            var customInstances = hqImport('app_manager/js/forms/custom_instances').wrap({
                customInstances: initialPageData('custom_instances'),
            });
            $('#custom-instances').koApplyBindings(customInstances);
        }

        // Case Management > Data dictionary descriptions for case properties
        $('.property-description').popover();

        // Advanced > XForm > Upload
        $("#xform_file_input").change(function(){
            if ($(this).val()) {
                $("#xform_file_submit").show();
            } else {
                $("#xform_file_submit").hide();
            }
        }).trigger('change');

        // Advanced > XForm > View
        $("#xform-source-opener").click(function(evt){
            if (evt.shiftKey) {
                // Shift+click: edit form source
                $(".source-readonly").hide();
                $(".source-edit").show();
                $.get($(this).data('href'), function (data) {
                    $("#xform-source-edit").text(data).blur();
                }, 'json');
            } else {
                // Plain click: view form source
                $(".source-edit").hide();
                $(".source-readonly").show();
                $("#xform-source").text("Loading...");
                $.get($(this).data('href'), function (data) {
                    var brush = new SyntaxHighlighter.brushes.Xml();    // eslint-disable-line eslint-dimagi/no-unblessed-new
                    brush.init({ toolbar: false });
                    // brush.getDiv seems to escape inconsistently, so I'm helping it out
                    data = data.replace(/&/g, '&amp;');
                    $("#xform-source").html(brush.getDiv(data));
                }, 'json');
            }
            $(".xml-source").modal();
        });
    });
});
