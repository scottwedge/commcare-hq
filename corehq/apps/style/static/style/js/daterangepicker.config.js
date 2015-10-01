$(function () {
    'use strict';
    $.fn.createBootstrap3DateRangePicker = function(
        range_labels, separator, startdate, enddate
    ) {
        var now = moment();
        var ranges = {};
        ranges[range_labels.last_7_days] = [
            moment().subtract('7', 'days').startOf('days')
        ];

        ranges[range_labels.last_month] = [
            moment().subtract('1', 'months').startOf('month'),
            moment().subtract('1', 'months').endOf('month')
        ];

        ranges[range_labels.last_30_days] = [
            moment().subtract('30', 'days').startOf('days')
        ];
        $(this).daterangepicker({
            showDropdowns: true,
            ranges: ranges,
            startDate: (!_.isNull(startdate)) ? new Date(startdate) : '',
            endDate: (!_.isNull(enddate)) ? new Date(enddate) : '',
            locale: {
                format: 'YYYY-MM-DD',
                separator: separator
            }
        });
    };
});
