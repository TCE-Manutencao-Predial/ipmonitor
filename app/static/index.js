 async function searchByVlan(){

            
            const vlanSelect = document.getElementById('vlanSelect');
            const vlan = encodeURIComponent(vlanSelect.value);  
            const response = await fetch(`api/start-check/${vlan}`)

            if(response.status !== 200){
                console.error('Falhou para obter os dados dos IPs');
                setInterval(searchByVlan, 5000);
                return;
            }
            else{
                mensagem_preliminar.textContent = ``;
                
                const data = await response.json();
                const tbody = document.getElementById('ipTableBody');
                tbody.innerHTML = '';  // Limpa a tabela antes de inserir novos elementos

                for (let i = 0; i < data.length; i += 3) {
                    const row = document.createElement('tr');

                    for (let j = 0; j < 3; j++) {
                        const descriptionCell = document.createElement('td');
                        const ipCell = document.createElement('td');
                        const statusCell = document.createElement('td');
                        const circle = document.createElement('span');

                        if (data[i + j]) {
                            descriptionCell.textContent = data[i + j].descricao;
                            ipCell.textContent = data[i + j].ip;
                            circle.classList.add('circle','red');
                        }

                        statusCell.appendChild(circle);
                        row.appendChild(descriptionCell);
                        row.appendChild(ipCell);
                        row.appendChild(statusCell);
                    }

                    tbody.appendChild(row);
                }
            }
        }

        document.getElementById("vlanSelect").addEventListener("change", function() {
            localStorage.setItem("selectedOption", this.value);
        });

        // When the page loads, retrieve and set the selected option from localStorage
        window.onload = function() {
            const savedOption = localStorage.getItem("selectedOption");
            if (savedOption) {
                document.getElementById("vlanSelect").value = savedOption;
            }
        };
        setInterval(searchByVlan, 30000);