var pages_info = {
	users: {
		fields: { id:["#user-user-name", "#user-user-id", "#user-user-password"], index:[1,3,4] },						
		selections: { id:["#user-city-side", "#user-privilege","#user-language"], index:[2,6,7] },
		textArea: { id:[], index:[] },
		databasehiddenFields: { id:"#admin-databseId", index:0 }
	},
	stations: {
		fields: {id:["#station-station-name"],index:[1]},						
		selections: {id: ["#station-city-side"],index: [2]}, 
		textArea:{id: [],index: []},
		databasehiddenFields: {id: "#admin-databseId",index: 0}
	},
	feeders: {
		fields: {id:["#feeder-feeder-name"],index:[1]},						
		selections: {id: ["#feeder-station-name"],index: [2]}, 
		textArea:{id: [],index: []},
		databasehiddenFields: {id: "#admin-databseId",index: 0}
	},
	files: {
		fields: {id: ["#updator-name","#update-from-search"],index:[5,6]},						
		selections: {id:["#subsation-list","#feeder-list"],index:[1,2]},
		textArea: {id:["#files-note"], index: [7]},
		databasehiddenFields: {id:"#admin-databseId", index: 0}
	},
	/* in upload page, there is no editing, so no need for index */
	upload: {
		fields: {id:["#editor-name","#editing-date","#input-note"], index: []},						
		selections: {id:["#subsation-list","#feeder-list"], index: []}, 
		textArea:{id:[], index: []},
		databasehiddenFields: {id:"#admin-databseId", index:null}
	}
};

var dictionary = {
	feeder: {English: "Feeder", Arabic: "اسم المغذي"},
	station: {English: "Station", Arabic: "أسم المحطة"},
	editor: {English: "Editor", Arabic: "اسم محدث المعلومات"},
	uploader: {English: "Uploader", Arabic: "اسم محمل المعلومات"},
	e_date: {English: "Editing Date", Arabic: "تاريخ التحديث"},
	u_date: {English: "Upload Date", Arabic: "تاريخ التحميل"},
	notes: {English: "Notes", Arabic: "الملاحظات"},
	login_id: {English: "Login ID", Arabic:"اسم الحساب"},
	pass: {English: "Password", Arabic: "كلمة المرور"},
	city_side: {English: "City Side", Arabic: "جانب المدينة"},
	privilege: {English: "Privilege", Arabic: "الصلاحيات"},
	language: {English: "Lanugage", Arabic: "اللغة"},
	to: {English: "To", Arabic: "الى"},
	review: {English: "Open", Arabic: "عرض"},
	del: {English: "Delete", Arabic: "حذف"},
	edit: {English: "Edit", Arabic: "تحديث"},
	add: {English: "Add", Arabic: "اضافة"},
	rst: {English: "Reset", Arabic: "مسح"},
	search: {English: "Search", Arabic: "بحث"},
	gis: {English: "GIS Department", Arabic: "قسم نظام المعلومات الجغرافية"},
	users_btn: {English: "Users", Arabic: "المستخدمين"},
	feeders_btn: {English: "Feeders", Arabic: "المغذيات"},
	stations_btn: {English: "Stations", Arabic: "المحطات"},
	files_btn: {English: "Files", Arabic: "الملفات"},
	logout: {English: "Logout", Arabic: "خروج"},
	upload: {English: "Upload", Arabic: "تحميل"},
	admin: {English: "Admin", Arabic: "المشرف"},
	c_date: {English: "Creation Date", Arabic: "تاريخ الانشاء"},
	file_upload: {English: "Choose File ...", Arabic: "اختيار الملف ..."},
}

document.addEventListener('DOMContentLoaded', function(){
	/* get the language to be used for user interface */
	var language = document.querySelector("#page-language").innerHTML;
	set_page_lanugage(language);
	/* Display messages only if there is previous Add, Update or delete */
	var messaageDiv = document.querySelector("#user-message");
	message = messaageDiv.innerHTML;
	if(message.trim()==="none"){
		messaageDiv.remove();
	}
	else{
		setTimeout(function(){messaageDiv.remove()}, 3000);
	}
	/* Set dictionary for the different pages */
	var page_name = document.querySelector("#page-name").innerHTML;
	var input_fields = pages_info[page_name].fields;
	var input_selections = pages_info[page_name].selections;
	var hidden_fields = pages_info[page_name].databasehiddenFields;
	var input_textAreas = pages_info[page_name].textArea;
	/* Set form action to the add route (default) */
	form = document.querySelector("form");
	form.action = document.querySelector("#form-submit-button").dataset.href;
	/* Load Listeners */
	form_submission(input_fields, input_selections);	
	edit_buttons_onClick(input_fields, input_selections, input_textAreas, hidden_fields, language);
	hide_unprivileged();
	addStyles();
});

function set_page_lanugage(language){
	if (language === "Arabic"){
		document.querySelector('html').style.direction = "rtl";
		document.querySelector('#js-navbar-nav-lang-adjust').className += " mr-auto";
		document.querySelector('#modal').style.direction = "ltr";
	}
	else{
		document.querySelector('html').style.direction = "ltr";
		document.querySelector('#js-navbar-nav-lang-adjust').className += " ml-auto";
	}
	document.querySelectorAll('.translate').forEach(function(element){
		dictionaryKey = element.dataset.key;
		element.innerHTML = dictionary[dictionaryKey][language];
	});
}

function hide_unprivileged(){
	var has_privilege = document.querySelector("#has-privilege").innerHTML;
	if(has_privilege == "False"){
		document.querySelectorAll('.hidden-for-unpriviledged').forEach(function(element){
		element.remove();
		});
	}
}

function edit_buttons_onClick(fields, selections, textAreas, hiddenFields, language){
	document.querySelectorAll('.row-edit-button').forEach(function(edit_button){
	    edit_button.onclick = function() {
	    	/* Change form action to the update route */
	    	form = document.querySelector("form");
	    	form.action = edit_button.dataset.href;
	    	/* Change the submit button text to "Edit", considering the language of the page*/
			document.querySelector("#form-submit-button").innerHTML = dictionary["edit"][language];
	    	/* Remove all previous validation data */
	    	remove_validation_info();
	    	/* populate the form fields with edited data */
	    	var tds = this.parentNode.parentNode.children;  	
	    	for (var i = 0; i < fields.id.length; i++) {
				document.querySelector(fields.id[i]).value = tds[fields.index[i]].innerHTML;   		
			} 
			/* populate the form selections with edit data */
	    	for (var j = 0; j < selections.id.length; j++) {
				select_object = document.querySelector(selections.id[j]);
				for(var k=0; k<select_object.length; k++){					 
					if(select_object[k].text === tds[selections.index[j]].innerHTML){
						select_object[k].selected = true;
					}
				}   		
			}
			for (var k = 0; k < textAreas.id.length; k++) {
				document.querySelector(textAreas.id[k]).innerHTML = tds[textAreas.index[k]].innerHTML;   		
			} 
			/* fill the hidden field of databaseId which will be used as reference of replacement in flask route */
			document.querySelector(hiddenFields.id).value = tds[hiddenFields.index].innerHTML;
			document.querySelectorAll('.remove-on-edit').forEach(function(element){
				element.remove();
			});
	    };
	});
}

function form_submission(fields, selections){
	form.addEventListener('submit', function(event) {
		/* Remove previous validations before submitting the new data */
		remove_validation_info();
		/* Check the form data, if it is not valid, it will not be submitted */
		if (!form_validation(fields, selections)) {
          event.preventDefault();
          event.stopPropagation();
        }
    });
}

/* Note: hidden fields are not validated */
function form_validation(fields, selections){
	/* Create a validation dictionary to add validation info it, the idea is to used it to insert the validation
		info only when the data is invalid */
	var valDic = [];
	/* the validation is true unless an invalid field will change it */
	var is_valid = true;
	/* If any of the fields is empty, then the data is not valid */
    for (var i = 0; i < fields.id.length; i++) {
    	if(document.querySelector(fields.id[i]).value === ""){
 			is_valid = false;
 			valDic.push({mesClass:"invalid-feedback", sibClass:"is-invalid", message:"invalid!", 
 				sibId: fields.id[i]});
    	}
    	else{
    		valDic.push({mesClass:"valid-feedback", sibClass:"is-valid", message:"Good", 
    			sibId: fields.id[i]});
    	}
	}
	for (var j = 0; j < selections.id.length; j++){
		element = document.querySelector(selections.id[j]);
		if(element.options[element.selectedIndex].text === ""){
			is_valid = false;
			valDic.push({mesClass:"invalid-feedback", sibClass:"is-invalid", message:"invalid!", 
				sibId: selections.id[j]});
		}
		else{
			valDic.push({mesClass:"valid-feedback", sibClass:"is-valid", message:"Good", 
				sibId: selections.id[j]});
    	}
	}
	/* Only add validation info if the data is invalid */
	if(!is_valid){
		for(var k=0; k < valDic.length; k++){
			add_validation_info(valDic[k].mesClass, valDic[k].sibClass, valDic[k].message, valDic[k].sibId);
		}
	}
	return is_valid;
}

function add_validation_info(message_class, sibling_class, message_text, sibling_id){
	/* Create new div with validation class and text */
    const newDiv = document.createElement('div');
    newDiv.className = message_class + " validation-message";
    newDiv.innerHTML = message_text;
    /* Choose the field where the validation will be put below it and add validation class to it */
    const sibling = document.querySelector(sibling_id);
    sibling.className += " "+ sibling_class;
    /* if the field to be validated has a previous validation, remove it */
    if(!sibling.classList.contains("validated-input")){
		sibling.className += " validated-input";
	}
	/* Add the validation new div below the field which will be validated */
    const parent = sibling.parentNode;
    parent.append(newDiv);
}

function remove_validation_info(){
	/* Remove all previous validation messages*/
	document.querySelectorAll('.validation-message').forEach(function(element){
		element.remove();
	});
	/* Remove previously added validation classes from input fields and selection*/
	document.querySelectorAll('.validated-input').forEach(function(element){
		if(element.classList.contains("is-invalid")){
			element.classList.remove("is-invalid")
		}
		else{
			element.classList.remove("is-valid");
		}
	});
}

/* Modal for user confirmation, I used JQuery because no easy way to do it with vanilla javascript */
$('#modal').on('show.bs.modal', function (e) {
	/* get the element that invoked the modal */
	var inovker = $(e.relatedTarget);
	/* add href to continue button */
	document.querySelector("#confirm-button").href = inovker.attr("data-href");
	/* add text to modal parts */
	document.querySelector("#modal-title").innerHTML = inovker.attr("data-messageTitle");
	document.querySelector("#modal-body").innerHTML = inovker.attr("data-messageBody");
	document.querySelector("#cancel-button").innerHTML = inovker.attr("data-messageCancel");
	document.querySelector("#confirm-button").innerHTML = inovker.attr("data-messageContinue");
});

function addStyles(){
	/* Adding p-2 class to all th */
	document.querySelectorAll('th').forEach(function(element){
		element.className += " p-2 h5";
	});
}