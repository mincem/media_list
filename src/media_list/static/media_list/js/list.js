$(document).ready(function () {
  document.detailView = new DetailView();

  $('.ml-row').click(renderDetailView);

  $("#filters").find('.filter-title').on('keyup', filterListByTitle);

  $(".magic-button").click(doMagic);
});

function renderDetailView() {
  let series = new MediaSeries($(this).data('series-id'));
  document.detailView.register(series);
  document.detailView.render();
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

class MediaSeries {
  constructor(id) {
    this.id = id;
  }
}

class DetailView {
  constructor() {
    this.mediaSeries = null;
    this.$modal = $('#details-modal');
  }

  register(mediaSeries) {
    this.mediaSeries = mediaSeries;
  }

  render() {
    if (this.mediaSeries === null) return;
    $.ajax({
      url: `/media_list/detail/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData)
      }
    });
  }

  display(htmlData) {
    this.$modal.find('.modal-content').html(htmlData);
    this.$modal.modal('show');
    $('#action-find-baka-id').click(() => {
      this.findBakaID()
    });
    $('#action-get-baka-data').click(() => {
      this.getBakaData()
    });
  }

  findBakaID() {
    $.ajax({
      url: `/media_list/get_baka_id/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData)
      }
    });
  }

  getBakaData() {
    $.ajax({
      url: `/media_list/get_baka_info/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData)
      }
    });
  }
}
