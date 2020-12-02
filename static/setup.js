
window.addEventListener( "load", function (){
    console.log('loaded')
})

function clear_menu(){
    // Clear menu options
    console.log('clear button pressed');


    document.getElementById("city-search").value = "";
    document.getElementById("city-id").value = "";
    document.getElementById("state-abbr").value = "";
    document.getElementById("country-abbr").value = "";
    document.getElementById("lat").value = "";
    document.getElementById("lon").value = "";

    // document.getElementById("thunderstorm").value = val;
    // document.getElementById("thunderstorm").checked = chx;

    // document.getElementById("drizzle").value = val;
    // document.getElementById("drizzle").checked = chx;

    // document.getElementById("rain").value = val;
    // document.getElementById("rain").checked = chx;

    // document.getElementById("snow").value = val;
    // document.getElementById("snow").checked = chx;

    // document.getElementById("atmosphere").value = val;
    // document.getElementById("atmosphere").checked = chx;

    // document.getElementById("clouds").value = val;
    // document.getElementById("clouds").checked = chx;

    // document.getElementById("clear").value = val;
    // document.getElementById("clear").checked = chx;
}