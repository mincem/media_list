$(document).ready(function () {
  let $interest_range = $('.interest-range');
  let $interest_value = $('.interest-value');

  $interest_value.val($interest_range.val());

  $interest_range.on('input', function () {
    $interest_value.val($interest_range.val());
  });
});
