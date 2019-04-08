$(document).ready(function () {
  $('.ml-row').click(function () {
    $.ajax({
      url: $(this).data('detail-url'),
      type: 'get',
      dataType: 'html',
      success: function (data) {
        let $detailsModal = $('#details-modal');
        $detailsModal.find('.modal-content').html(data);
        $detailsModal.modal('show');
      }
    });
  });

  $("#filters").find('.filter-title').on('keyup', function () {
    let value = $(this).val().toLowerCase();
    $('#media-list').find('tbody').find('tr').filter(function () {
      $(this).toggle($(this).find('.ml-cell-title').text().toLowerCase().indexOf(value) > -1)
    });
  });
});
