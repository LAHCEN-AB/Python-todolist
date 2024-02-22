function plop() {
    alert("plop");
}

function myFunction(divid) {
    document.getElementById(divid).innerHTML = "Paragraph changed."+new Date().getMinutes()+":"+ new Date().getSeconds();
}