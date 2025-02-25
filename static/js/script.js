function searchBooks() {
    let input = document.getElementById('search-input').value.toLowerCase();
    let books = document.getElementsByClassName('book-item');

    Array.from(books).forEach(book => {
        let title = book.querySelector('.book-title').textContent.toLowerCase();
        if (title.includes(input)) {
            book.style.display = '';
        } else {
            book.style.display = 'none';
        }
    });
}
function showEditForm(button) {
            var reviewId = button.getAttribute('data-review-id');
            var editForm = document.getElementById('edit-form-' + reviewId);
            if (editForm.style.display === 'none') {
                editForm.style.display = 'block';
            } else {
                editForm.style.display = 'none';
            }
}
function validateLoginForm() {
            var email = document.getElementById('email').value;
            var password = document.getElementById('password').value;

            if (email === '') {
                alert('Мора да внесете емаил.');
                return false;
            }

            if (password === '') {
                alert('Мора да внесете лозинка.');
                return false;
            }


            var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(email)) {
                alert('Внесете валиден емаил.');
                return false;
            }

            return true;
        }

        function validateRegisterForm() {
            var name = document.getElementById('name').value;
            var surname = document.getElementById('surname').value;
            var email = document.getElementById('email').value;
            var password = document.getElementById('password').value;
            var confirmPassword = document.getElementById('confirm_password').value;

            if (name === '' || surname === '' || email === '' || password === '' || confirmPassword === '') {
                alert('Сите полиња мора да бидат пополнети.');
                return false;
            }

            var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(email)) {
                alert('Внесете валиден емаил.');
                return false;
            }

            if (password !== confirmPassword) {
                alert('Лозинките не се совпаѓаат.');
                return false;
            }

            if (password.length < 6) {
                alert('Лозинката мора да има минимум 6 карактери.');
                return false;
            }

            return true;
}
