// if(document.getElementById('check_all').clicked == true)
// {
//    alert("button was clicked");
// }
// document.getElementById('check_all').onclick = function() {
//     alert("button was clicked");
//  }​;​

var checkbox_toggle = true;

window.addEventListener( "load", function (){
    console.log('loaded')
})


function toggle_menu(){
    // Toggle between all checkboxes checked and not
    console.log('button pressed');

    var val;
    var chx;

    if (checkbox_toggle == true) {
        val = "False";
        chx = false;
        checkbox_toggle = false;
    } else {
        val = "True";
        chx = true;
        checkbox_toggle = true;
    }
    // console.log(checkbox_toggle);
    // console.log(val);
    // console.log(chx);

    // console.log(document.querySelectorAll("input"));
    // console.log(document.getElementById("thunderstorm").value);
    // console.log(document.getElementById("thunderstorm").checked);
    document.getElementById("thunderstorm").value = val;
    document.getElementById("thunderstorm").checked = chx;

    document.getElementById("drizzle").value = val;
    document.getElementById("drizzle").checked = chx;

    document.getElementById("rain").value = val;
    document.getElementById("rain").checked = chx;

    document.getElementById("snow").value = val;
    document.getElementById("snow").checked = chx;

    document.getElementById("atmosphere").value = val;
    document.getElementById("atmosphere").checked = chx;

    document.getElementById("clouds").value = val;
    document.getElementById("clouds").checked = chx;

    document.getElementById("clear").value = val;
    document.getElementById("clear").checked = chx;
}
