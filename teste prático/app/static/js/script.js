// Função para exibir a imagem de perfil selecionada pelo usuário
function previewProfilePicture(event) {
    const imageElement = document.getElementById('profile-picture-preview');
    imageElement.src = URL.createObjectURL(event.target.files[0]);
}
