frappe.ready(function() {
	// bind events here
	frappe.web_form.after_load = (frm) => {
		console.log("hello");
	}

})
