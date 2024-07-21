$(document).ready(function(){

    document.getElementById("selectAllBtn").addEventListener('click', ()=>{
        for (let i of Array.from(document.getElementById("agreementContainer").querySelectorAll('input[type="checkbox"]'))) {
            i.checked = true;
        }
    });

    document.getElementById("infoDutyBtn").addEventListener('click', ()=>{
        $('#infoDutyModal').modal();
    });

});