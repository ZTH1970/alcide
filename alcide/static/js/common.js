function delete_prompt(text) {
  var r = prompt(text + '\n Pour cela veuillez entrer DEL');
  if (r.toLowerCase().replace(/^\s+|\s+$/g, '') == 'del') {
    return true;
  } else {
    return false;
  }
}

function init_datepickers(on) {
    $('.datepicker-date', on).datepicker({dateFormat: 'd/m/yy', showOn: 'button'});
    $('.datepicker input[type=text]', on).datepicker({dateFormat: 'd/m/yy', showOn: 'button'});
}
