// Login Form

const showPasswordCheckbox = document.getElementById("show-password");

if (showPasswordCheckbox) {
    showPasswordCheckbox.addEventListener("change", () => {
        const passwords = document.querySelectorAll(".password");
        passwords.forEach(password => {
            if (showPasswordCheckbox.checked) {
                password.type = "text";
            } else {
                password.type = "password";
            }
        });
    });
}


document.addEventListener("DOMContentLoaded", function() {
    const editIcons = document.querySelectorAll(".edit");
    const modalTitle = document.getElementById("transactionModalLabel");
    const form = document.getElementById("transaction-form");
    const closeBtn = document.getElementById("close-btn");
    const deleteBtn = document.getElementById("delete-btn");
    const addBtn = document.getElementById("add-btn");
    const saveBtn = document.getElementById("save-btn");

    if (editIcons) {
        editIcons.forEach(icon => {
            icon.addEventListener("click", async (event) => {
                const transactionId = event.target.parentElement.parentElement.id.replace('transaction-', '');
                modalTitle.textContent = "Edit Transaction";
                closeBtn.style.display = "none";
                deleteBtn.style.display = "inline-block";

                try {
                    const response = await fetch(`/edit-transaction/${transactionId}`, {
                        method: "GET"
                    });

                    const data = await response.json();

                    if (data.success) {
                        const transaction = data.transaction;
                        console.log(transaction)

                        form.elements["description"].value = transaction[0]["category"];
                        form.elements["price"].value = transaction[0]["amount"];
                        form.elements["date"].value = transaction[0]["date"];

                        saveBtn.dataset.transactionId = transaction[0]["id"];
                        deleteBtn.dataset.transactionId = transaction[0]["id"];
                        console.log(saveBtn.dataset.transactionId);

                    } else {
                        alert("Failed to fetch transaction details for editing.");
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred while fetching transaction details for editing.');
                }
            });
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener("click", async () => {
            const formData = new FormData(form);

            const transactionId = saveBtn.dataset.transactionId;
            console.log(transactionId)

            try {
                let response;
                if (transactionId) {
                    response = await fetch(`/edit-transaction/${transactionId}`, {
                        method: "POST",
                        body: formData
                    });
                } else {
                    response = await fetch("/add-transaction", {
                        method: "POST",
                        body: formData
                    });
                }

                const data = await response.json();

                if (data.success) {
                    const transactionModal = bootstrap.Modal.getInstance(document.getElementById('transactionModal'));
                    transactionModal.hide();

                    if (transactionId) {
                        const editedRow = document.getElementById(transactionId);
                        if (editedRow) {
                            editedRow.innerHTML = `
                                <td><i class="fas fa-edit edit" data-bs-toggle="modal" data-bs-target="#transactionModal"></i>${data.transaction[0]["category"]}</td>
                                <td>P${data.transaction[0]["amount"]}</td>
                                <td>${data.transaction[0]["date"]}</td>
                            `;
                        }
                    } else {
                        const noTransactionsRow = document.querySelector('table tbody tr td[colspan="3"]');
                        if (noTransactionsRow) {
                            noTransactionsRow.parentElement.remove();
                        }

                        const tbody = document.querySelector('table tbody');
                        const newRow = document.createElement('tr');
                        newRow.id = `transaction-${data.transaction.id}`;
                        newRow.innerHTML = `
                            <td><i class="fas fa-edit edit"></i>${data.transaction.category}</td>
                            <td>P${data.transaction.amount}</td>
                            <td>${data.transaction.date}</td>
                        `;
                        tbody.appendChild(newRow);
                    }
                } else {
                    alert("Failed to save transaction. Please try again later.");
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while saving the transaction.');
            }
        });
    }

    if (deleteBtn) {
        deleteBtn.addEventListener("click", async () => {
            const transactionId = deleteBtn.dataset.transactionId;

            try {
                const response = await fetch(`/delete-transaction/${transactionId}`, {
                    method: "POST"
                });

                const data = await response.json();

                if (data.success) {
                    const transactionModal = bootstrap.Modal.getInstance(document.getElementById('transactionModal'));
                    transactionModal.hide();

                    form.reset();

                    const deletedRow = document.getElementById(`${transactionId}`);

                    if (deletedRow) {
                        deletedRow.remove();
                    }
                    
                    const noTransactionsRow = document.querySelector('table tbody tr td[colspan="3"]');
                    const transactionsCount = document.querySelectorAll("table tbody tr");
                    if (!noTransactionsRow && transactionsCount.length < 1) {
                        document.querySelector("table tbody").innerHTML = `<td colspan="3" class="text-center">No transactions</td>`
                    }

                } else {
                    alert("Failed to delete transaction, please try again later.");
                }
            } catch (error) {
                console.error("Error: ", error);
                alert("An error occurred.")
            }
        });
    }

    if (addBtn) {
        addBtn.addEventListener("click", () => {
            modalTitle.textContent = "Add Transaction";
            form.reset();
            saveBtn.removeAttribute("data-transaction-id");
            deleteBtn.style.display = "none";
            closeBtn.style.display = "inline-block";
        });
    }
});
