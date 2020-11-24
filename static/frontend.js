

$(document).ready(function() {
    $(window).keydown(function(event){
      if(event.keyCode == 13) {
        event.preventDefault();
        return false;
      }
    });
});

$("#get_data").click(function(e){
    console.log(e)
    var dump_list = document.getElementById('dump_list');
    var html = "";
    data = $.get("/dump_testing", function(data, status){
        console.log("Data: " + data + "\nStatus: " + status);
        console.log(data[0])
        console.log(data[1])
        console.log(data[0]['name'])
        data.forEach(function(item, index) {
            console.log(item, index);
            html += "<tr>" + item + "</tr>";
            
            // dump_list[index] = item;
        })

        // for (const property in data) {
        //     console.log(`${property}: ${object[property]}`);
        // }
    // return data
    // dump_list.innerHTML = data;
    console.log(html)
    // dump_list.innerHTML = html;
    document.getElementById("new_dump").innerHTML = "a string";
    })
    console.log("Data: " + data + "\nStatus: " + status);
    console.log(data[0])
    // console.log(data[0]['name'])
    // console.log(data[0][0])
    // console.log(data)
    // console.log(Object.values(data))
    // console.log(data[0])
    // console.log(data['db_name'])
    // console.log(data.db_name)
    // console.log(data['env'])
    // for (const property in data) {
    //     console.log(`${property}: ${object[property]}`);
    // }
});