document.addEventListener("DOMContentLoaded",()=>{
 const input=document.getElementById("resume"), name=document.getElementById("fileName");
 if(input) input.addEventListener("change",()=>{name.textContent=input.files[0]?input.files[0].name:"No file selected"});
 document.querySelectorAll(".alert").forEach(a=>setTimeout(()=>a.remove(),4000));
});