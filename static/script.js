//------------------------------localizador---------------------------------//
function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(sendLocation);
  } else {
    alert('A geolocalização não é suportada por este navegador.');
  }
}

function sendLocation(position) {
  const latitude = position.coords.latitude;
  const longitude = position.coords.longitude;
  const radius = document.getElementById('distancia').value;

  // Redirecionar para a rota /parking com os parâmetros de latitude e longitude como parâmetros de query
  parametros =
    '?latitude=' + latitude + '&longitude=' + longitude + '&radius=' + radius;

  goToLoc('/mostraEstacionamentos', parametros);
}
//--------------------------------------------------------------------------//

//------------------------------novaVaga------------------------------------//
function converterEnderecoParaLatLng() {
  const geocoder = new google.maps.Geocoder();
  const endereco = document.getElementById('address').value;

  geocoder.geocode({ address: endereco }, function (results, status) {
    if (status === google.maps.GeocoderStatus.OK) {
      const latitude = results[0].geometry.location.lat();
      const longitude = results[0].geometry.location.lng();

      document.getElementById('longitude').value = longitude;
      document.getElementById('latitude').value = latitude;

      // Centralizar o mapa na localização geocodificada
      mapa.setCenter({ lat: latitude, lng: longitude });
      mapa.setZoom(15);
      // Colocar um marcador no mapa
      new google.maps.Marker({
        position: { lat: latitude, lng: longitude },
        map: mapa,
      });
      showPerID('confirm');
    } else {
      alert(
        'A geocodificação não foi bem-sucedida pelo seguinte motivo: ' + status
      );
    }
  });
}
//--------------------------------------------------------------------------//

//-----------------------------------alugar---------------------------------//
function atualizaPreco(preco) {
  const entrada = new Date(document.getElementById('dataEntrada').value);
  const saida = new Date(document.getElementById('dataSaida').value);

  const numDias = (new Date(saida) - new Date(entrada)) / (1000 * 60 * 60 * 24);
  const today = new Date();

  if (saida == 'Invalid Date') {
  } else {
    if (entrada < today) {
      alert('Data inicial anterior a data atual');
      document.getElementById('botaoConfirma').disabled = true;
      document.getElementById('conta').hidden = true;
    } else {
      if (numDias <= 0) {
        alert('Datas invalidas (0 ou menos dias)');
        document.getElementById('botaoConfirma').disabled = true;
        document.getElementById('conta').hidden = true;
      } else {
        document.getElementById('botaoConfirma').disabled = false;
        document.getElementById('conta').hidden = false;

        const precoDias = preco * numDias;
        const taxa = precoDias * 0.02;
        const precoTotal = precoDias + taxa;

        document.getElementById('precoTotal').textContent =
          precoTotal.toLocaleString(undefined, {
            minimumFractionDigits: 2,
          });

        document.getElementById('precoTotal2').textContent =
          precoDias.toLocaleString(undefined, {
            minimumFractionDigits: 2,
          });

        document.getElementById('numdias').textContent = numDias;
        document.getElementById('preco').textContent = preco;
        document.getElementById('taxa').textContent = taxa.toLocaleString(
          undefined,
          {
            minimumFractionDigits: 2,
          }
        );
      }
    }
  }
}
//--------------------------------------------------------------------------//

//-----------------------------------checkout-------------------------------//
function liberarVaga(vagaId) {
  fetch('/liberarVaga', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `vaga_id=${vagaId}`,
  })
    .then((response) => {
      if (response.redirected) {
        window.location.href = response.url;
      }
    })
    .catch((error) => {
      console.error('Erro ao liberar vaga:', error);
    });
}

function avaliarVaga(vagaId, nota) {
  fetch('/avaliarVaga', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `vaga_id=${vagaId}&nota=${nota}`,
  })
    .then((response) => {
      if (response.redirected) {
        document.getElementById('rating').disabled = true;
        window.location.href = response.url;
      }
    })
    .catch((error) => {
      console.error('Erro ao avaliar vaga:', error);
    });
}
//---------------------------------------------------------------------------//

//-----------------------------------uso geral-------------------------------//

function showPerID(id) {
  elemento = document.getElementById(id);

  if (elemento.style.display == 'none') {
    elemento.style.display = 'flex';
  }
}

function completaEspacos() {
  console.log(getParam('long'));
  switchValue('long', getParam('long'));
  switchValue('lat', getParam('lat'));
}

function getById(isso) {
  return document.getElementById(isso).value;
}

function switchValue(isso, valor) {
  document.getElementById(isso).value = valor;
}

function getParam(palavra) {
  let url = new URL(window.location.href);
  return url.searchParams.get(palavra);
}

function goToLoc(location, parameters) {
  let url = new URL(window.location.href);
  if (parameters == undefined) {
    window.location.href = location;
  } else {
    window.location.href = location + parameters;
  }
}
//---------------------------------------------------------------------------//

//--------------------------mostraConfirmaVagas------------------------------//
function mostra(id) {
  document.getElementById(id).hidden = false;
}

function esconde(id) {
  document.getElementById(id).hidden = true;
}
