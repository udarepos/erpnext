// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
// frappe.provide('frappe.phone_call');
frappe.ui.form.on('Call Log', {
	refresh: function(frm) {
		frm.events.setup_recording_audio_control(frm);
		const incoming_call = frm.doc.type == 'Inbound';
		frm.add_custom_button(incoming_call ? __('Callback'): __('Call Again'), () => {
			const number = incoming_call ? frm.doc.from : frm.doc.to;
			const token = "ATCAPtkn_578180ebbb2129e0aad08417d8bd0ac4e57ba614f09c232beaf800bd5e1e7735";
			const client = new Africastalking.Client(token);
			// frappe.phone_call.handler(number, frm);
			client.call(number);
			// frappe.xcall('erpnext.erpnext_integrations.africastalking_integration.make_a_call', {
			// 	'callTo': number
			// })
		});
	},
	setup_recording_audio_control(frm) {
		const recording_wrapper = frm.get_field('recording_html').$wrapper;
		if (!frm.doc.recording_url || frm.doc.recording_url == 'null') {
			recording_wrapper.empty();
		} else {
			recording_wrapper.addClass('input-max-width');
			recording_wrapper.html(`
				<audio
					controls
					src="${frm.doc.recording_url}">
				</audio>
			`);
		}
	}
});

var script = document.createElement('script');
document.head.appendChild(script);
// script.onload = refresh;
script.src = "https://unpkg.com/africastalking-client@1.0.7/build/africastalking.js";