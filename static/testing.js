$("#submit_door").click(function(e){
    console.log("Toggle the Door");
    var pin = $("#PIN")[0].value;
    if (pin == "") {
        alert("You must enter a pin first");
        return;
    }
    // $.ajax({
    //     url   : '/door',
    //     type  : 'post',
    //     data  : {"pin": pin}, // data to be submitted
    //     success: function(response){
    //         alert("Toggling Door (video lags by about 5-10 seconds)"); // do what you like with the response
    //         },
    //     error: function(response){
    //         console.log(response);
    //         alert(response['status'] + ": " + response['responseJSON']['detail']);
    //     }
    // });
});

$("#submit_light").click(function(e){
    console.log("Toggle the Light new");

    url = 'http://localhost:8010/html_testing2'

    fetch(url)
    .then((resp) => resp.json())
    .then(function(data) {
        console.log(data)
        document.getElementById('testdata').value = data;
        // document.write("Testdata is " + data)
    })
    .catch()

    console.log(url)

    // var pin = $("#PIN")[0].value;
    // const response = fetch('http://localhost:8010/html_testing2');
    // const myJson = response.json();
    // console.log(myJson)
    // if (pin == "") {
    //     alert("You must enter a pin first");
    //     return;
    // }
    // $.ajax({
    //     url   : '/light',
    //     type  : 'post',
    //     data  : {"pin": pin}, // data to be submitted
    //     success: function(response){
    //         alert("Toggling Light (video lags by about 5-10 seconds)"); // do what you like with the response
    //         },
    //     error: function(response){
    //         console.log(response);
    //         alert(response['status'] + ": " + response['responseJSON']['detail']);
    //     }
    // });
});

// $(document).ready(function() {
//     $(window).keydown(function(event){
//       if(event.keyCode == 13) {
//         event.preventDefault();
//         return false;
//       }
//     });
// });

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

// $("#get_data").click(function(e){
//     console.log("Get data run");
//     $.ajax({
//         url     : '/state',
//         type    : 'get',
//         success: function(response){
//             console.log('get success');
//         },
//         error: function(response){
//             console.log('it errored');
//         }
//     })
// });

// $(function(){
//     $('#get_data').click(function() {
//         console.log('get data clicked')
//     })
// })
