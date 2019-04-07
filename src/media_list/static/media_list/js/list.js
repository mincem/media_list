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
});
