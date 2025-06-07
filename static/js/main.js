document.addEventListener('DOMContentLoaded', function() {
    // Обработка лайков для постов
    document.querySelectorAll('.post-like-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            fetch(`/post/${postId}/like`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                const likesCount = this.querySelector('.likes-count');
                likesCount.textContent = data.likes;
                this.classList.toggle('liked', data.liked);
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Обработка лайков для комментариев
    document.querySelectorAll('.comment-like-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.dataset.commentId;
            fetch(`/comment/${commentId}/like`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                const likesCount = this.querySelector('.likes-count');
                likesCount.textContent = data.likes;
                this.classList.toggle('liked', data.liked);
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Автоматическое закрытие алертов
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Предпросмотр аватара
    const avatarInput = document.querySelector('#avatar');
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('#avatar-preview');
                    if (preview) {
                        preview.src = e.target.result;
                    }
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Подтверждение удаления
    document.querySelectorAll('.delete-confirm').forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить это?')) {
                e.preventDefault();
            }
        });
    });

    // Обработка тегов
    const tagInput = document.querySelector('#tags');
    if (tagInput) {
        tagInput.addEventListener('keydown', function(e) {
            if (e.key === ',') {
                e.preventDefault();
                const value = this.value.trim();
                if (value) {
                    this.value = value + ', ';
                }
            }
        });
    }
}); 