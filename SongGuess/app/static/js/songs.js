    function changed(token) {
     let btn = `<button class="btn btn-primary btn-sm" onclick="saveSong('${token}');"><i class="bi bi-floppy"></i></button>`;
        $(`#state-${token}`).html(btn);
    }

    function saveSong(token) {
        let artist = $(`#artist-${token}`).val();
        let title = $(`#title-${token}`).val();
        let year = $(`#year-${token}`).val();
        $.ajax({
            url: '/songs/save',
            type: 'POST',
            data: JSON.stringify({ 'artist': artist, 'title': title, 'year': year, 'token': token }),
            contentType: 'application/json',
            success: function(response) {
                if (response['error'] == 0) {
                    console.log(`Song saved successfully.`);
                    $(`#year-${token}`).removeClass('bg-danger');
                    if(response['data'].artist !== "Unknown") {
                        $(`#artist-${token}`).removeClass('bg-danger');
                    }
                    if(response['data'].title !== "Unknown") {
                        $(`#title-${token}`).removeClass('bg-danger');
                    }
                    $(`#state-${token}`).html('<div class="badge bg-success ms-1 me-1"><i class="bi bi-check me-1"></i>OK</div>');
                } else {
                    console.error(`Error saving song ${response['message']}`);
                    $(`#state-${token}`).html('<div class="badge bg-danger ms-1 me-1"><i class="bi bi-exclamation-triangle me-1"></i>ERROR</div>');
                }
            },
            error: function(xhr, status, error) {
                console.error(`Error while saving song ${token}.`);
                $(`#state-${token}`).html('<div class="badge bg-danger ms-1 me-1"><i class="bi bi-exclamation-triangle me-1"></i>ERROR</div>');
            }
        });
    }