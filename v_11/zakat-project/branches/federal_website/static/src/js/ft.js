
'use strict';

window.location.hash="no-back-button";
window.location.hash="Again-No-back-button";
window.onhashchange=function(){window.location.hash="B";}

function ValidateFile1(file) {
  var filename = file.files[0].name;
  document.getElementById("file_name1").value = filename;
document.getElementById("file_name1").readOnly = true;
 document.getElementById("file1_div").style.display = "block";  
        var FileSize = file.files[0].size / 1024 ; // in kB
        if (FileSize > 250) {
            alert('حجم الملف كبير، اقصى حجم يجب ان يكون  KB 150');
        } else {

        }
    }

function ValidateFile2(file) {
  var filename = file.files[0].name;
  document.getElementById("file_name2").value = filename;
document.getElementById("file_name2").readOnly = true;
 document.getElementById("file2_div").style.display = "block";  
        var FileSize = file.files[0].size / 1024 ; // in kB
        if (FileSize > 250) {
            alert('حجم الملف كبير، اقصى حجم يجب ان يكون  KB 150');
        } else {

        }
    }

function ValidateFile3(file) {
  var filename = file.files[0].name;
  document.getElementById("file_name3").value = filename;
document.getElementById("file_name3").readOnly = true;
 document.getElementById("file3_div").style.display = "block";  
        var FileSize = file.files[0].size / 1024 ; // in kB
        if (FileSize > 250) {
            alert('حجم الملف كبير، اقصى حجم يجب ان يكون  KB 150');
        } else {

        }
    }

function ValidateFile4(file) {
  var filename = file.files[0].name;
  document.getElementById("file_name4").value = filename;
document.getElementById("file_name4").readOnly = true;
 document.getElementById("file4_div").style.display = "block";  
        var FileSize = file.files[0].size / 1024 ; // in kB
        if (FileSize > 250) {
            alert('حجم الملف كبير، اقصى حجم يجب ان يكون  KB 150');
        } else {

        }
    }
function folowing(){

if (document.getElementById('folow_natio').checked) {
 document.getElementById("na_fol").style.display = "block";
 document.getElementById("fol_folwing").style.display = "none";
 document.getElementById("passport_fol").style.display = "none";

 document.getElementById('n_nat').value = 'natio';
}

else if (document.getElementById('pass_fol').checked) {
  document.getElementById("passport_fol").style.display = "block";
  document.getElementById("fol_folwing").style.display = "none";
  document.getElementById("na_fol").style.display = "none";
  document.getElementById('n_nat').value = 'passp';

}

else{
 document.getElementById("na_fol").style.display = "none";
 document.getElementById("fol_folwing").style.display = "block";
 document.getElementById('n_nat').value = 'ref';
   document.getElementById("passport_fol").style.display = "none";


}

}
function followingValidation(){

    var radio_val = document.getElementById('n_nat').value;

    var natio = document.getElementById("national_folow").value;
    var passpo = document.getElementById("pass_fol").value;
    var refrence = document.getElementById("follow_num").value;

    if (document.getElementById("req_n").value == 'natio_wrong'){
      document.getElementById("natio_wrong").style.display = "block";
      document.getElementById("national_folow").value = '';

    }
    
    if (radio_val == 'natio'){

      var numbers = /^[0-9]+$/;
      if(!natio.match(numbers) || natio.length != 11)
      {
        document.getElementById("natio_msg").style.display = "block";
        document.getElementById("natio_validate").value = 'False';

          }
    else{
      document.getElementById("natio_validate").value = 'True';
      document.getElementById("natio_msg").style.display = "none";
    }
    }

   /* else if (radio_val == 'passp'){
      var numbers = /^[0-9]+$/;
      if(!passpo.match(numbers) || passpo.length != 9)
      {

        document.getElementById("natio_msg").style.display = "none";
        document.getElementById("natio_validate").value = 'True';
        document.getElementById("pass_validate").value = 'False';
        document.getElementById("pass_msg").style.display = "block";


          }
    else{
      document.getElementById("pass_validate").value = 'True';
      document.getElementById("pass_msg").style.display = "none";
    }
    }


    else{
      if (refrence.charAt(0) != 'R' && refrence.charAt(1) != 'E'){
        document.getElementById("natio_msg").style.display = "none";
        document.getElementById("natio_validate").value = 'True';
        document.getElementById("fol_validate").value = 'False';
        document.getElementById("fol_msg").style.display = "block";

      }
      else{
 document.getElementById("fol_validate").value = 'True';
      document.getElementById("fol_msg").style.display = "none";
    
      }

}*/
}

$(document).ready(function(){
    $("#myBtn").click(function(){
        $("#myModal").modal();
    });
});

var modal = document.getElementById('id01');

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}


$(document).ready(function(){
    $("#myBtn2").click(function(){
        $("#myModal2").modal();
    });
});




function validateAlreasyReg()
{
  var amount = document.getElementById("treatment_amount").value;
  var numbers = /^[0-9]+$/;
if(!amount.match(numbers)) 
{
  document.getElementById("amount_v").value = 'False';
  document.getElementById("amount_validate").style.display = "block";
  }
else{
  document.getElementById("amount_validate").style.display = "none";
  document.getElementById("amount_v").value = 'True';

    }

 }
function validateRegistration()
{
  
  var f = document.getElementById("first_name").value;
  var s = document.getElementById("second_name").value;
  var l = document.getElementById("third_name").value;
  var fo = document.getElementById("forth_name").value;

  var ph = document.getElementById("phone").value;
  var job = document.getElementById("job").value;
  var house = document.getElementById("house_no").value;
  var amount = document.getElementById("treatment_amount").value;
  var numbers = /^[0-9]+$/;

  if(!f.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$") 
  || !s.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$")
  || !l.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$")
  || !fo.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$")){

  document.getElementById("name_v").value = 'False';
  document.getElementById("name_validate").style.display = "block";
  }
else{
  document.getElementById("name_validate").style.display = "none";
  document.getElementById("name_v").value = 'True';
    }

if(!ph.match(numbers) || ph.length != 10 || ph.charAt(0) != 0){
  document.getElementById("phone_v").value = 'False';
  document.getElementById("phone_validate").style.display = "block";
}
else{
  document.getElementById("phone_validate").style.display = "none";
  document.getElementById("phone_v").value = 'True';
}

if(!job.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$")) 
{
  document.getElementById("job_v").value = 'False';
  document.getElementById("job_validate").style.display = "block";
  }
else{
  document.getElementById("job_validate").style.display = "none";
  document.getElementById("job_v").value = 'True';
    }

if(!house.match(numbers)) 
{
  document.getElementById("house_v").value = 'False';
  document.getElementById("house_validate").style.display = "block";
  }
else{
  document.getElementById("house_validate").style.display = "none";
  document.getElementById("house_v").value = 'True';

    }

if(!amount.match(numbers)) 
{
  document.getElementById("amount_v").value = 'False';
  document.getElementById("amount_validate").style.display = "block";
  }
else{
  document.getElementById("amount_validate").style.display = "none";
  document.getElementById("amount_v").value = 'True';

    }

  }

 function show(){
  var option = document.getElementById("nationality").value;
  
  var nationality_value = document.getElementById("nationality").value ;
  var passport_div = document.getElementById("passport_div");
  var national_number_div = document.getElementById("national_number_div");
    if (nationality_value == 'sd'){
        national_number_div.style.display = "block";
        passport_div.style.display = "none";
   } 

   else {
          national_number_div.style.display = "none";
       passport_div.style.display = "block";
    }
   
 }

function validateForm()
{
    var n = document.getElementById("nationality").value;
    var z = document.getElementById("national_n").value;
    var p = document.getElementById("passport").value;
    var s = document.getElementById("session_start");


// national number
if (n === 'sd'){

    var numbers = /^[0-9]+$/;
      if(!z.match(numbers) || z.length != 11)
      {
        document.getElementById("national_msg").style.display = "block";
        document.getElementById("national_n").focus();
        document.getElementById("national_validate").value = 'False';


                }
    else{
      document.getElementById("national_validate").value = 'True';
      document.getElementById("national_msg").style.display = "none";
      document.getElementById("session_start").value = 'True';
    }
}

// Passport 9 
if (n === 'other'){
     if(p.length != 9)
      {
        document.getElementById("passport_msg").style.display = "block";
        document.getElementById("passport").focus();
        document.getElementById("passport_validate").value = 'False';

                }
    else{
      document.getElementById("passport_validate").value = 'True';
      document.getElementById("passport_msg").style.display = "none";
      document.getElementById("session_start").value = 'True';

    }
  }
}





function validate_bill() {
  var isChecked = false;
  if (document.getElementById('bill').checked) {
    isChecked = true;
    console.log(isChecked);
 
} 
else {
    isChecked = false;
    console.log(isChecked);
  }
}

function validate_medical() {
  var isChecked = false;
  if (document.getElementById('medical').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
    console.log(isChecked);
  }
}

function validate_medical() {
  var isChecked = false;
  if (document.getElementById('medical').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
    console.log(isChecked);
  }
}


function validate_review() {
  var isChecked = false;
  if (document.getElementById('review').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
    console.log(isChecked);
  }
}


function validate_check() {
  var isChecked = false;
  if (document.getElementById('check').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
    console.log(isChecked);
  }
}

function validate_study() {
  var isChecked = false;
  if (document.getElementById('study').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
    console.log(isChecked);
  }
}

function validate_commission() {
  var isChecked = false;
  if (document.getElementById('commission').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
    console.log(isChecked);
  }
}

function validate_abroad_cost() {
  var isChecked = false;
  if (document.getElementById('abroad_cost').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
    console.log(isChecked);
  }
}


function validate_passport_co() {
  var isChecked = false;
  if (document.getElementById('passport_co').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
    console.log(isChecked);
  }
}

function validate_tickets() {
  var isChecked = false;
  if (document.getElementById('tickets').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
    console.log(isChecked);
  }
}


function validate_visa() {
  var isChecked = false;
  if (document.getElementById('visa').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
  }
}


function validate_conversion_replacement() {
  var isChecked = false;
  if (document.getElementById('conversion_replacement').checked) {
    isChecked = true;  
} 
else {
    isChecked = false;
  }
}
/*

var q = new Date();
var m = q.getMonth();
var d = q.getDay();
var y = q.getFullYear();
var dd = y +'/'+ m +'/' + d;
var date = new Date(y,m,d);

var a = b_date.split('-');
var date = new Date (a[2], a[1] - 1,a[0]);//using a[1]-1 since Date object has month from 0-11
var Today = new Date();

if (date > Today){
  document.getElementById("birth_v").value = 'False';
  document.getElementById("birth_validate").style.display = "block";
}
else{
 document.getElementById("birth_validate").style.display = "none";
  document.getElementById("birth_v").value = 'True';
}*/
// function InvalidMsg(textbox) {
//     if (textbox.value == '') {
//         textbox.setCustomValidity('Required email address');
//     }
//     else if (textbox.validity.typeMismatch){
//         textbox.setCustomValidity('please enter a valid email address');
//     }
//     else {
//        textbox.setCustomValidity('');
//     }
//     return true;
// }
/*
!f.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$") 
  || !s.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$")
  || !l.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$")
  || !fo.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$")*/
  /* function preventBack(){
  window.history.forward();
}
  setTimeout("preventBack()", 0);

  window.onunload=function(){
    null
  };
*/