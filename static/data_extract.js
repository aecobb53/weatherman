// const btn = document.querySelector('form');

// function sendData( data ) {
//     console.log( 'Sending data' );

//     const XHR = new XMLHttpRequest();

//     let urlEncodedData = "",
//         urlEncodedDataPairs = [],
//         name;

//     // Turn the data object into an array of URL-encoded key/value pairs.
//     for( name in data ) {
//     urlEncodedDataPairs.push( encodeURIComponent( name ) + '=' + encodeURIComponent( data[name] ) );
//     }

//     // Combine the pairs into a single string and replace all %-encoded spaces to 
//     // the '+' character; matches the behaviour of browser form submissions.
//     urlEncodedData = urlEncodedDataPairs.join( '&' ).replace( /%20/g, '+' );

//     // Define what happens on successful data submission
//     XHR.addEventListener( 'load', function(event) {
//     console.log( 'Yeah! Data sent and response loaded.' );
//     } );

//     // Define what happens in case of error
//     XHR.addEventListener( 'error', function(event) {
//     alert( 'Oops! Something went wrong.' );
//     } );

//     // Set up our request
//     XHR.open( 'POST', '/dump/search' );

//     // Add the required HTTP header for form data POST requests
//     XHR.setRequestHeader( 'Content-Type', 'application/x-www-form-urlencoded' );

//     // Finally, send our data.
//     console.log(urlEncodedData)
//     XHR.send( urlEncodedData );
// }

// btn.addEventListener( 'click', function() {
//     sendData( {thunderstorm:true, drizzle:false} );
//     // sendData( {thunderstorm:document.querySelector('thunderstorm')} );
// } )



// window.addEventListener( "load", function () {
//     function sendData() {
//       const XHR = new XMLHttpRequest();
  
//       // Bind the FormData object and the form element
//       const FD = new FormData( form );
  
//       // Define what happens on successful data submission
//       XHR.addEventListener( "load", function(event) {
//         alert( event.target.responseText );
//       } );
  
//       // Define what happens in case of error
//       XHR.addEventListener( "error", function( event ) {
//         alert( 'Oops! Something went wrong.' );
//       } );
  
//       // Set up our request
//       XHR.open( "POST", "https://example.com/cors.php" );
  
//       // The data sent is what the user provided in the form
//       XHR.send( FD );
//     }
   
//     // Access the form element...
//     const form = document.getElementById( "myForm" );
  
//     // ...and take over its submit event.
//     form.addEventListener( "submit", function ( event ) {
//       event.preventDefault();
  
//       sendData();
//     } );
//   } );










// const EF = document.getElementById( "extract_form" )

// function sendData() {
//     console.log('sending data');

//     const XHR = new XMLHttpRequest();

//     let urlEncodedData = "",
//         urlEncodedDataPairs = [],
//         name;

//     // console.log(urlEncodedData);
//     // console.log(urlEncodedDataPairs);
//     // console.log(name);

//     // urlEncodedData = "/dump_testing?"

//     const FD = new FormData( EF );

//     // Turn the data object into an array of URL-encoded key/value pairs.
//     for(var pair of FD.entries()) {
//         // console.log(pair[0] + ', ' + pair[1]);
//         urlEncodedDataPairs.push( pair[0] + '=' + pair[1] );
//     }

//     // Combine the pairs into a single string and replace all %-encoded spaces to 
//     // the '+' character; matches the behaviour of browser form submissions.
//     urlEncodedData += urlEncodedDataPairs.join( '&' ).replace( /%20/g, '+' );

//     // Define what happens on successful data submission
//     XHR.addEventListener( 'load', function(event) {
//         console.log( 'Yeah! Data sent and response loaded.' );
//     } );

//     // Define what happens in case of error
//     XHR.addEventListener( 'error', function(event) {
//         console.log( 'Oops! Something went wrong.' );
//         console.log(XHR.responseText);
//     } );

//     // Set up our request
//     XHR.open( 'POST', '/dump/search' );

//     // Add the required HTTP header for form data POST requests
//     // XHR.setRequestHeader( 'Content-Type', 'application/x-www-form-urlencoded' );

//     // Finally, send our data.
//     XHR.send( FD );
//     // XHR.send( urlEncodedData );

//     console.log(urlEncodedData);
//     console.log(urlEncodedDataPairs);
//     console.log(name);

// }

// window.addEventListener("load", function() {
//     console.log('Page loaded')
// })

// EF.addEventListener( "submit", function( event ) {
//     console.log('form submitted')
//     event.preventDefault()
//     sendData()
// })




$(function() {
    $('#extract_form').submit(function(event) {
        event.preventDefault();

        var formEl = $(this);
        var submitButton = $('input[type=submit]', formEl);

        $.ajax({
        type: 'POST',
        url: formEl.prop('action'),
        accept: {
            javascript: 'application/javascript'
        },
        data: formEl.serialize(),
        beforeSend: function() {
            submitButton.prop('disabled', 'disabled');
        }
        }).done(function(data) {
        submitButton.prop('disabled', false);
        });
    });
});




//   const XHR = new XMLHttpRequest();
    
//   // Bind the FormData object and the form element
//   const FD = new FormData( form );

//   let urlEncodedData = "",
//       urlEncodedDataPairs = [],
//       name;

// console.log(urlEncodedData)
// console.log(urlEncodedDataPairs)

//   console.log(form)
//   console.log(FD)
//   for(var pair of FD.entries()) {
//       console.log(pair[0] + ', ' + pair[1]);
//       urlEncodedDataPairs.push( pair[0] + '=' + pair[1] );
//   }
//   urlEncodedData = urlEncodedDataPairs.join( '&' ).replace( /%20/g, '+' );
//   console.log(urlEncodedData)
//   console.log(urlEncodedDataPairs)
// //   for(var pair of FD.entries()) {
// //     console.log(pair[0]+ ', '+ pair[1]); 





// $("#get_data").click(function(e){
// // $(document).ready(function () { 
//     console.log('Getting data from DB')
//     console.log("form stuff")
//     console.log(document.querySelector("form"))

//     // sendData( {test:'ok'} );

//     // FETCHING DATA FROM JSON FILE 
//     // $.getJSON("/dump_testing",  
//     $.getJSON("/dump",  
//     function (data) { 
//         console.log(data)
//         var weather = ''; 

//         // ITERATING THROUGH OBJECTS 
//         $.each(data, function (key, value) { 
//             console.log("key: " + key + ", value: " + value)

//             //CONSTRUCTION OF ROWS HAVING 
//             // DATA FROM JSON OBJECT 

//             weather += '<tr>'; 
            
//             weather += '<td>' + 
//                 value.name + '</td>';

//             weather += '<td>' + 
//                 value.sky + '</td>';

//             weather += '<td>' + 
//                 value.sky_id + '</td>';

//             weather += '<td>' + 
//                 value.sky_desc + '</td>';

//             weather += '<td>' + 
//                 value.temp + '</td>';

//             weather += '<td>' + 
//                 value.wind + '</td>';

//             weather += '<td>' + 
//                 value.time + '</td>';

//             weather += '</tr>'; 


//             // weather += '<tr>'; 
//             // weather += '<td>' +  
//             //     value.name + '</td>'; 

//             // weather += '<td>' +  
//             //     value.sky + '</td>'; 

//             // weather += '<td>' +  
//             //     value.sky_id + '</td>'; 

//             // weather += '<td>' +  
//             //     value.temp + '</td>'; 

//             // weather += '</tr>'; 
//         }); 
        
//         //INSERTING ROWS INTO TABLE  
//         $('#table').append(weather); 
//     }); 
    
//     // // FETCHING DATA FROM JSON FILE 
//     // $.getJSON("/dump_testing",  
//     //         function (data) { 
//     //     var student = ''; 

//     //     // ITERATING THROUGH OBJECTS 
//     //     $.each(data, function (key, value) { 

//     //         //CONSTRUCTION OF ROWS HAVING 
//     //         // DATA FROM JSON OBJECT 
//     //         student += '<tr>'; 
//     //         student += '<td>' +  
//     //             value.GFGUserName + '</td>'; 

//     //         student += '<td>' +  
//     //             value.NoOfProblems + '</td>'; 

//     //         student += '<td>' +  
//     //             value.TotalScore + '</td>'; 

//     //         student += '<td>' +  
//     //             value.Articles + '</td>'; 

//     //         student += '</tr>'; 
//     //     }); 
          
//     //     //INSERTING ROWS INTO TABLE  
//     //     $('#table').append(student); 
//     // }); 
// }); 
