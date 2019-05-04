$(document).ready(function () {
  $('.ml-row').click(showDetailsView);

  $("#filters").find('.filter-title').on('keyup', filterListByTitle);

  $(".magic-button").click(doMagic);
});

function showDetailsView() {
  $.ajax({
    url: $(this).data('detail-url'),
    type: 'get',
    dataType: 'html',
    success: openDetailsModal
  });
}

function openDetailsModal(data) {
  let $detailsModal = $('#details-modal');
  $detailsModal.find('.modal-content').html(data);
  $detailsModal.modal('show');
}

function filterListByTitle(event) {
  let searchInput = $(event.target).val().toLowerCase();
  $('#media-list').find('tbody').find('tr').filter(function () {
    $(this).toggle($(this).find('.ml-cell-title').text().toLowerCase().indexOf(searchInput) > -1)
  });
}

function doMagic() {
  $.ajax({
    url: $(this).data('magic-url'),
    type: 'get',
    dataType: 'json',
    success: function (data) {
      alert(data['result']);
    }
  });
}
