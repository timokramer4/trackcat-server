var previewImg, resultImg;

function initCrop(fileDialogId, previewImgId, resultImgId, minSize, startSelection) {
    setModal();
    previewImg = $(`#${previewImgId}`)[0];
    resultImg = $(`#${resultImgId}`)[0];

    var fileDialog = $(`#${fileDialogId}`);
    fileDialog.change(function () {
        var file = this.files[0];
        if (file.size > 0) {
            var reader = new FileReader();
            reader.onload = function () {
                previewImg.src = reader.result;
                $(`#${previewImgId}`).Jcrop({
                    onChange: updatePreview,
                    onSelect: updatePreview,
                    bgColor: 'black',
                    bgOpacity: .2,
                    minSize: minSize,
                    setSelect: startSelection,
                    aspectRatio: minSize[0] / minSize[1]
                });
            };
            reader.readAsDataURL(file);
            $('#imageResizer').modal('toggle');
        }
    });

    $("#saveNewProfileImg").on("click", function () {
        /* Update hidden base64 string */
        var base64Img = resultImg.toDataURL("image/jpeg").split(',')[1];
        $('#base64Img').val(base64Img);
    });
}

function setModal() {
    var modal = document.createElement("div");
    modal.innerHTML = `<!-- Modal window: Image resizer -->
    <div id="imageResizer" class="modal" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Neues Profilbild festlegen</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body text-center">
            <form id="changeProfileImg" action="changeProfileImg" method="POST">
                <div>
                    <img id="newProfileImagePreview" style="max-width: 100%;" />
                </div>
                <br>
                <input type="text" id="x" name="coord_x" style="display: none" />
                <input type="text" id="y" name="coord_y" style="display: none" />
                <input type="text" id="x2" name="coord_x2" style="display: none" />
                <input type="text" id="y2" name="coord_y2" style="display: none" />
                <input type="text" id="w" name="size_w" style="display: none" />
                <input type="text" id="h" name="size_h" style="display: none" />
                <canvas id="resultNewProfileImg" width="320" height="320"></canvas>
                <input id="base64Img" name="base64Img" type="text" style="display: none" />        
                <div class="modal-footer">
                    <button id="cancelNewProfileImg" type="button" class="btn btn-secondary" data-dismiss="modal">Abbruch</button>
                    <button id="saveNewProfileImg" type="submit" class="btn btn-primary">Profilbild speichern</button>
                </div>
            </form>
        </div>
      </div>
    </div>`;
    document.getElementById("main").appendChild(modal);
}

function setCords(c) {
    $('#x').val(c.x);
    $('#y').val(c.y);
    $('#x2').val(c.x2);
    $('#y2').val(c.y2);
    $('#w').val(c.w);
    $('#h').val(c.h);
}

function updatePreview(c) {
    if (parseInt(c.w) > 0) {
        var rx = 220 / c.w, ry = 220 / c.h;
    }

    setCords(c);

    var context = resultImg.getContext("2d");
    var $img = $(previewImg),
        imgW = previewImg.width,
        imgH = previewImg.height;

    console.log("Breite: " + imgW + "/" + $img.width());
    console.log("Höhe: " + imgH + "/" + $img.height());

    var ratioY = imgH / $img.height(),
        ratioX = imgW / $img.width();

    var getX = $('#x').val() * ratioX,
        getY = $('#y').val() * ratioY,
        getWidth = $('#w').val() * ratioX,
        getHeight = $('#h').val() * ratioY;

    context.drawImage(previewImg, getX, getY, getWidth, getHeight, 0, 0, 320, 320);
}