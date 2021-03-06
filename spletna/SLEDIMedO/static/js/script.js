/* It initializes on click action for elements inside header */
let elemInHeader = document.getElementById("topNav").getElementsByTagName("a");

/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function responsiveHeader() {
    let x = document.getElementById("topNav");
    if (x.className === "topnav") {
        x.className += " responsive";
    } else {
        x.className = "topnav";
    }
}

/* When a page loads it calls colorHeader function */
window.onload = colorHeader;

/* Function paints menu tab */
function colorHeader(event) {
	let path = (window.location.pathname).split("/").pop();
	for (let i = 0; i < elemInHeader.length; i++){
		if (path == elemInHeader[i].href.split("/").pop())
			elemInHeader[i].classList.add("active");
	}	
}