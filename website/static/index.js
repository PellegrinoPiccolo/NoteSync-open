function closeAlert(){
    document.getElementById("alert").remove();
}

function deleteNote(noteId){
    var choice = confirm("You want eleminate this note?")
    if(choice){
        fetch('/delete-note',{
            method: "POST",
            body: JSON.stringify({noteId: noteId }),
        }).then( (_res) => {
            window.location.href="/my-notes"
        });
    }
}

function copyTextNote(id) {
    var r = document.createRange();
    r.selectNode(document.getElementById(id));
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(r);
    document.execCommand('copy');
    window.getSelection().removeAllRanges();
}

function deleteGroup(groupId){
    var choice = confirm("You want eleminate this group?")
    if(choice){
        fetch('/delete-group',{
            method: "POST",
            body: JSON.stringify({groupId: groupId }),
        }).then( (_res) => {
            window.location.href="/my-groups"
        });
    }
}

$("#infoIcon").hover(function(){
    $('#textInfo').toggleClass('text_info_hide')
    $('#textInfo').toggleClass('text_info_active')
  });

function leaveGroup(groupId){
    var choice = confirm("You want leave this group?")
    if(choice){
        fetch('/leave-group',{
            method: "POST",
            body: JSON.stringify({groupId: groupId}),
        }).then((_res)=>{
            window.location.href="/my-groups"
        })
    }
}

function removeUser(groupId, userId){
    var choice = confirm("You want eject this uses?")
    if(choice){
        fetch('/remove-user',{
            method: "POST",
            body: JSON.stringify({groupId: groupId, userId: userId}),
        }).then((_res)=>{
            window.location.href="/members-group/" + groupId
        })
    }
}

function openMenu(id){
    id.classList.add('link_menu_active')
}

function closeMenu(id){
    id.classList.remove('link_menu_active')
}

$('.owl-carousel').owlCarousel({
    loop:false,
    margin:10,
    responsiveClass:true,
    responsive:{
        0:{
            items:2,
            nav:false,
            loop:false
        },
        600:{
            items:2,
            nav:true
        },
        1000:{
            items:5,
            nav:true,
            loop:false
        }
    }
})

function deleteFolder(id){
    var choiche = confirm("Do you want to delete this folder? Deleting it will delete all the notes in it")
    if(choiche){
        fetch("/delete-folder",{
            method: "POST",
            body: JSON.stringify({ folderId: id}),
        }).then((_res)=>{
            window.location.href="/my-notes"
        })
    }
}

function stampaContenuto() {
    // Apri la finestra di stampa
    window.print();
}

// Aggiungi un evento di click al tuo pulsante o a un altro elemento per attivare la funzione
document.getElementById('pulsanteStampa').addEventListener('click', stampaContenuto);

function abbreviaTesto(testo, lunghezzaMassima) {
    if (testo.length > lunghezzaMassima) {
        return testo.substring(0, lunghezzaMassima) + "...";
    } else {
        return testo;
    }
}