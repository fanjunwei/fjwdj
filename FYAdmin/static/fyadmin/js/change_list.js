/**
 * Created by fanjunwei003 on 14/11/22.
 */
function object_table_select() {
    var object_table = $('#object_table');
    var top_check = object_table.find('thead').find('input[type=checkbox]');
    var item_checks = object_table.find('tbody').find('input[type=checkbox]');
    top_check.change(function () {

        if ($(this).is(":checked") == true) {

            item_checks.attr("checked", true);
            item_checks.prop("checked", true);
        }
        else {
            item_checks.attr("checked", false);
            item_checks.prop("checked", false);

        }
        item_checks.change();
    });


    item_checks.change(function () {

        var row = $(this).parent().parent();

        if ($(this).is(":checked") == true) {
            row.attr('class', 'info');
        }
        else {
            row.attr('class', '');
        }
    });

    if (/msie/.test(navigator.userAgent.toLowerCase())) {
        top_check.click(function () {
            this.blur();
            this.focus();
        });

        item_checks.click(function () {
            this.blur();
            this.focus();
        });
    }

}
function delete_confirm() {
    $('[name=delete]').click(function () {
        $('#delModal').modal('show');
        return false;
    });

}

$(
    function () {
        object_table_select();
        delete_confirm();
    }
);
