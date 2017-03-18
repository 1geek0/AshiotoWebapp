var selectAllState = true;
$(".selectall").click(function () {
    if (selectAllState) {
        $(".selectitem").removeAttr("disabled");
        selectAllState = false;
    } else {
        $(".selectitem").attr("checked", "checked");
        $(".selectitem").attr("disabled", "disabled");
        selectAllState = true;
    }
});
