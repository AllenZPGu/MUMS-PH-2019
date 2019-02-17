function createRow(compRow) {
	var indivRegForm = document.getElementById("indivRegForm");
	var noChild = indivRegForm.childNodes.length;
	

	var newRow = document.createElement("div");
	newRow.className = "form-row formset_row"
	newRow.id = "indivRow_" + noChild.toString();

	// Member label
	var memberLabel = document.createElement("div");
	memberLabel.className = "col-1";
	memberLabel.innerHTML = "Member " + noChild.toString()
	newRow.appendChild(memberLabel);

	// Name field
}



function initIndivField() {
	indivRegForm = document.getElementById("indivRegForm");

}

