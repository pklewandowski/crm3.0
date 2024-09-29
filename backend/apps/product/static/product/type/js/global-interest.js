$(document).ready(function () {

    $('.btn-save').click(function () {

        Alert.questionWarning(
            "Czy na pewno wprowadzić oprocentowanie (operacji nie będzie można cofnąć) ?",
            '',
            ()=>{
                $('form').submit();
            }
        )
    });
});