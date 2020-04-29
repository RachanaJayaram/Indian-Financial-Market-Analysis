URL = "http://127.0.0.1:5000/api2"

$(function () {
  $('#submit').bind('click', function () {
    $.getJSON(URL, {
      symbol: $('input[name="symbol"]').val(),
      start: $('input[name="start"]').val(),
      end: $('input[name="end"]').val()
    }, function (data) {
      console.log("Falling",data.result["falling"]);
      console.log("Growing",data.result["growing"]);
      Falling=data.result["falling"];
      Growing=data.result["growing"];
      renderdivs(Falling, Growing);
    });
    return false;
  });
});

function renderdivs(falling,growing){
    var col1 = document.getElementById("col1");
    var head1=document.createElement("h1");
    head1.innerHTML="Growing Scripts"
    col1.appendChild(head1)
    for(var i=0;i<growing.length;i++)
    {
        var itemdiv=document.createElement("div");
        itemdiv.innerHTML=growing[i];
        col1.appendChild(itemdiv);
    }
    var col2 = document.getElementById("col2");
    var head2=document.createElement("h1");
    head2.innerHTML="Falling Scripts"
    col2.appendChild(head2)
    for(var i=0;i<falling.length;i++)
    {
        var itemdiv=document.createElement("div");
        itemdiv.innerHTML=falling[i];
        col2.appendChild(itemdiv);
    }
}