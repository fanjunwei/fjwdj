/**
 * Created by fanjunwei on 14/11/23.
 */

$(function () {
    $('[role=datetimepicker-date]').datetimepicker({
        format: 'yyyy-MM-dd',
        language: 'zh-CN',
        pickDate: true,
        pickTime: false,
        hourStep: 1,
        minuteStep: 15,
        secondStep: 30,
        inputMask: true
    });

    $('[role=datetimepicker-time]').datetimepicker({
        format: 'hh:mm:ss',
        language: 'zh-CN',
        pickDate: false,
        pickTime: true,
        hourStep: 1,
        minuteStep: 15,
        secondStep: 30,
        inputMask: true
    });
});