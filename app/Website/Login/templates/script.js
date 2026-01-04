
let username;
let password;

document.getElementById("submit").onclick = function(){
    username = document.getElementById("username").value;
    password = document.getElementById("password").value;

    console.log(username)
    console.log(password)
}