const store = require('google-play-scraper');
const XLSX = require('xlsx');
const FN = "ScrapeGoogleStore.xlsx"
const READ_AMOUNT = 200

// read file
let wb = XLSX.readFile(FN)
let ws = wb.Sheets["Parameters"];
let ws2 = wb.Sheets["Apps"];

// read parameters
let readAll = false
if (ws[`B1`] && ["YES","Y"].includes(ws[`B1`].v.toUpperCase())) {
  readAll = true
}

// read column A with categories
const maxRow = 10000
let arrColl = []
let arrCat = []
for (i=4; i<=maxRow; i++) {
  if (ws[`A${i}`] === undefined) {
    break
  }
  arrColl.push(ws[`A${i}`].v)
  arrCat.push(ws[`B${i}`].v)
}
// console.log(arrColl)
// console.log(arrCat)

// read column AW app-id
let arrIDApp = []
for (i=2; i<=maxRow; i++) {
  if (ws2[`AW${i}`] === undefined) {
    break
  }
  arrIDApp.push(ws2[`AW${i}`].v)
}
let nextFreeRow = i
// console.log(arrIDApp.length)
// console.log(nextFreeRow)
// process.exit(1)

async function getStoreCollection(coll,cat) {
  let result = await store.list({
    collection: store.collection[coll],
    category: store.category[cat],
    num: READ_AMOUNT,
    fullDetail: true
  })
  // console.log(result.length)
  return result
}

async function main () {
  // let rowNumber = 2
  let arrWorkedOn = []
  for (i=0; i<arrColl.length; i++) {
    let erg = await getStoreCollection(arrColl[i],arrCat[i])
    // console.log(`Check Erg: ${erg.values()}`)
    // console.log(erg[0])
    // console.log(Object.keys(erg[0]))
    for (entry in erg) {}
    erg.forEach(function (item,index) {   
      // check if allready worked on in this run for the app-id
      if (!arrWorkedOn.includes(item.appId)) {
        // check rowNumber for the actual to include row
        if (arrIDApp.includes(item.appId)) {
          const tmpFunc = (elem) => elem == item.appId
          rowNumber = arrIDApp.findIndex(tmpFunc) + 2
        } else {
          rowNumber = nextFreeRow
          nextFreeRow += 1
        }

        // console.log(item)
        XLSX.utils.sheet_add_aoa(ws2, [[arrColl[i]]], {origin: `A${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[arrCat[i]]], {origin: `B${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.title]], {origin: `C${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.description]], {origin: `D${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.descriptionHTML]], {origin: `E${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.summary]], {origin: `F${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.installs]], {origin: `G${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.minInstalls]], {origin: `H${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.maxInstalls]], {origin: `I${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.score]], {origin: `J${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.scoreText]], {origin: `K${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.ratings]], {origin: `L${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.reviews]], {origin: `M${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.histogram]], {origin: `N${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.price]], {origin: `O${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.free]], {origin: `P${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.currency]], {origin: `Q${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.priceText]], {origin: `R${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.offersIAP]], {origin: `S${rowNumber}`});                        
        XLSX.utils.sheet_add_aoa(ws2, [[item.IAPRange]], {origin: `T${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.size]], {origin: `U${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.androidVersion]], {origin: `V${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.androidVersionText]], {origin: `W${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.developer]], {origin: `X${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.developerId]], {origin: `Y${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.developerEmail]], {origin: `Z${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.developerWebsite]], {origin: `AA${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.developerAddress]], {origin: `AB${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.privacyPolicy]], {origin: `AC${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.developerInternalID]], {origin: `AD${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.genre]], {origin: `AE${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.genreId]], {origin: `AF${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.familyGenre]], {origin: `AG${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.familyGenreId]], {origin: `AH${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.icon]], {origin: `AI${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.headerImage]], {origin: `AJ${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.screenshots.toString()]], {origin: `AK${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.video]], {origin: `AL${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.videoImage]], {origin: `AM${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.contentRating]], {origin: `AN${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.contentRatingDescription]], {origin: `AO${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.adSupported]], {origin: `AP${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.released]], {origin: `AQ${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[Date(item.updated)]], {origin: `AR${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.version]], {origin: `AS${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.recentChanges]], {origin: `AT${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.comments.toString()]], {origin: `AU${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.editorsChoice]], {origin: `AV${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.appId]], {origin: `AW${rowNumber}`});
        XLSX.utils.sheet_add_aoa(ws2, [[item.url]], {origin: `AX${rowNumber}`});

        // // check if in-app-purchase keywords are in the description
        // let tmpArrSearchResults = []
        // let tmpDesc = item.description.toLowerCase()
        // searchWord.forEach((elem,idx) => {
        //   if (tmpDesc.includes(elem)) {        
        //     tmpArrSearchResults.push(elem)
        //   }
        // })
        // XLSX.utils.sheet_add_aoa(ws2, [[tmpArrSearchResults.toString()]], {origin: `V${rowNumber}`});                                  
        
        console.log(`${item.appId} ${item.title} prepared for XLSX...`)
        arrWorkedOn.push(item.appId)
      }

      // process.exit(1)      
    })
    XLSX.writeFile(wb, FN);                            
  }
}

main().catch(err => console.log(err))












