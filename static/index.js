// display last modification

if (document.querySelector(".last_mod")){
    let LastModif = new Date(document.lastModified);
    document.querySelector(".last_mod").innerHTML = "last mod: " + LastModif.toDateString();
    };
    
// bluring page on nav button click
    function blur(selector,value){
        let matches = document.querySelector(selector);
        matches.style.opacity = value;
    }
    
    let bluring = 1;
    const identy = ".container";
    const low = "0.4";
    const high = "1";
    
    document.querySelector(".navbar-toggler").addEventListener('click', function(){
        switch(bluring){
            case 1:
                blur(identy,low);
                bluring = 0
                break;
    
            case 0:
                blur(identy,high)
                bluring = 1;
                break;
            }
    });

   