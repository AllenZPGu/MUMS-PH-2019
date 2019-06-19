function centreAllCheckboxes() {
	var inputArray = document.getElementsByClassName("centred-checkbox");
	for (var i = 0; i < inputArray.length; i++) {
		inputArray[i].parentElement.parentElement.setAttribute("style", "text-align:center; vertical-align:middle;");
	}
}

centreAllCheckboxes();