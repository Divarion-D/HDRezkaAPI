$('#search-button').on('click', function () {
	getResult()
});

$('#search-input').on('keyup', function (e) {
	if (e.keyCode === 13) {
		getResult()
	}
});

const ApiUrl = window.location.origin + "/api";


function getPlayer(id, trans_id){
	console.log(id)
	console.log(trans_id)
}

$('#movie-list').on('click', '.see-details', function (e) {
	$('.modal-body').html('');
	$('#loading-detail').html(`
		<div class="d-flex justify-content-center">
				<div class="spinner-border" role="status">
					<span class="sr-only">Loading...</span>
			</div>
		</div>
	`);
	$.ajax({
		url: ApiUrl + "/details",
		type: 'get',
		dataType: 'json',
		data: {
			'id': $(this).data('id')
		},
		success: function (result) {
			$('#loading-detail').html('');
			const modalBody = $('.modal-body');
			const container = $('<div class="container-fluid"></div>');
			const row1 = $('<div class="row"></div>');
			const row2 = $('<div class="row"></div>');
			const col1 = $('<div class="col-md-4"></div>');
			const col2 = $('<div class="col-md-8"></div>');
			const col3 = $('<div class="col-md-12 mt-2"></div>');
			const col4 = $('<div class="col-md-12" id="player"></div>');
			const ul = $('<ul class="list-group"></ul>');

			const img = $('<img src="' + result.imageUrl + '" class="img-fluid mb-3" onError="this.onerror=null;this.src=\'error.jpg\';">');
			const liTitle = $('<li class="list-group-item"><h4>' + result.title + '</h4></li>');
			
			col1.append(img);
			row1.append(col1);
			
			ul.append(liTitle);
			if (result.description != null) {
				const liRelease = $('<li class="list-group-item"><b>Description:</b> ' + result.description + '</li>');
				ul.append(liRelease);
			}
			if (result.data.release != null) {
				const liRelease = $('<li class="list-group-item"><b>Release Date:</b> ' + result.data.release + '</li>');
				ul.append(liRelease);
			}
			if (result.data.genre != null) {
				const liGenre = $('<li class="list-group-item"><b>Genre:</b> ' + result.data.genre + '</li>');
				ul.append(liGenre);
			}
			if (result.data.country != null) {
				const liCountry = $('<li class="list-group-item"><b>Country:</b> ' + result.data.country + '</li>');
				ul.append(liCountry);
			}
			if (result.data.director != null) {
				const liDirector = $('<li class="list-group-item"><b>Director:</b> ' + result.data.director + '</li>');
				ul.append(liDirector);
			}

			col2.append(ul);
			row1.append(col2);
			container.append(row1);

			$.each(result.translations_id, function (i, translation) {
				// add button in translations
				const btn = $('<button class="btn btn-primary m-1" onclick="getPlayer(' + result.id +','+ translation.id + ')" >'+translation.name+'</button>');
				col3.append(btn);
			})
			col4.append(img)

			row2.append(col3);
			row2.append(col4);
			container.append(row2);
			modalBody.append(container);
		}
	});
});

function getResult() {
	$('#movie-list').html('')

	$('#loading').html(`<div class="row1 mb-5" id="covid-box">
						<div class="col-md-12">
							<div class="d-flex justify-content-center">
								<div class="spinner-grow text-success" role="status">
									<span class="sr-only">Loading...</span>
								</div>
								<div class="spinner-grow text-danger" role="status">
									<span class="sr-only">Loading...</span>
								</div>
								<div class="spinner-grow text-warning" role="status">
									<span class="sr-only">Loading...</span>
								</div>
							</div>
						</div>
						<div class="col-md-12 justify-content-center">
							<p class="text-center pt-3"><strong>Loading result...</strong></p>
						</div>
					</div>
				`)

	$.ajax({
		url: ApiUrl + "/search",
		type: 'get',
		dataType: 'json',
		data: {
			'query': $('#search-input').val()
		},
		success: function (result) {
			console.log(result);
			totalResults = result.length
			if (totalResults > 0) {
				$('#movie-total').html(`
				<p> <strong>Total result</strong> : `+ totalResults + ` movie <br> <small><i>*) Only showing max 10 movie list in a row1.</i></small></p>
					`)

				$.each(result, function (i, data) {
					$('#loading').html('');
					$('#movie-list').append(`
					<div class="col-sm-6 col-md-6 col-lg-3">
						<div class="card mb-3 justify-content-center">
							<img src="`+ data.imageUrl + `" class="bd-placeholder-img card-img-top img-fluid miniimg" width="100%" height="225" alt="poster" onError="this.onerror=null;this.src='error.jpg';">
								<div class="card-body d-flex flex-column">
									<h5 class="card-title">` + data.title + `</h5>
									<h6 class="card-subtitle mb-2 text-muted">`+ data.year + `</h6>

									<a href="#" class="btn btn-dark btn-block align-self-end see-details mt-auto" data-toggle="modal" data-target="#exampleModal" data-id="`+ data.id + `">Подробнее</a>
								</div>
						</div>
						</div>
				`)
				})

			} else {
				$('#movie-total').html('');
				$('#loading').html('');
				$('#loading-detail').html('');
				$('#movie-list').html(`
				<div class="col-md-12">
					<h1 class="text-center">`+ result + `<h1>
					</div>
						`)
			}
		}
	});
}
