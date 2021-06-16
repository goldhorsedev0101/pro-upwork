const store = require('app-store-scraper');
const XLSX = require('xlsx');
const FN = "ScrapeAppStore.xlsx"
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

// let searchWord = []
// if (ws[`D1`]) {
//   searchWord = ws[`D1`].v.split(",")
//   searchWord = searchWord.map(x => x.trim().toLowerCase())
// }

// read column A with categories
let maxRow = 10000
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

// read existing apps-ids
let arrIDExis = []
for (i=2; i<=maxRow; i++) {
  if (ws2[`C${i}`] === undefined) {
    break
  }
  arrIDExis.push(ws2[`C${i}`].v)
}
nextFreeRow = i
// console.log(arrIDExis)

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
  for (i=0; i<arrColl.length; i++) {
    let erg = await getStoreCollection(arrColl[i],arrCat[i])
    // console.log(`Check Erg: ${erg.values()}`)
    // console.log(erg[0])
    // console.log(Object.keys(erg[0]))
    for (entry in erg) {}
    erg.forEach(function (item,index) {    
      // check row-number to write data
      if (arrIDExis.includes(item.id)) {
        const dummyFunction = (elem) => elem === item.id
        rowNumber = arrIDExis.findIndex(dummyFunction) + 2     
      } else {
        rowNumber = nextFreeRow
        nextFreeRow += 1
      }
      // console.log(item.id)
      // console.log(rowNumber)
      // console.log(item)

      // write data to xlsx
      XLSX.utils.sheet_add_aoa(ws2, [[arrColl[i]]], {origin: `A${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[arrCat[i]]], {origin: `B${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.id]], {origin: `C${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.appId]], {origin: `D${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.title]], {origin: `E${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.url]], {origin: `F${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.description]], {origin: `G${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.icon]], {origin: `H${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.genres.toString()]], {origin: `I${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.genreIds.toString()]], {origin: `J${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.primaryGenre]], {origin: `K${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.primaryGenreId]], {origin: `L${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.contentRating]], {origin: `M${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.languages.toString()]], {origin: `N${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.size]], {origin: `O${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.requiredOsVersion]], {origin: `P${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.released]], {origin: `Q${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.updated]], {origin: `R${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.releaseNotes]], {origin: `S${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.version]], {origin: `T${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.price]], {origin: `U${rowNumber}`});                        
      XLSX.utils.sheet_add_aoa(ws2, [[item.currency]], {origin: `W${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.free]], {origin: `X${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.developerId]], {origin: `Y${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.developer]], {origin: `Z${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.developerUrl]], {origin: `AA${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.developerWebsite]], {origin: `AB${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.score]], {origin: `AC${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.reviews]], {origin: `AD${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.currentVersionScore]], {origin: `AE${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.currentVersionReviews]], {origin: `AF${rowNumber}`});
      XLSX.utils.sheet_add_aoa(ws2, [[item.supportedDevices.toString()]], {origin: `AG${rowNumber}`});
      // XLSX.utils.sheet_add_aoa(ws2, [[item.screenshots.toString()]], {origin: `AH${rowNumber}`});
      // XLSX.utils.sheet_add_aoa(ws2, [[item.ipadScreenshots]], {origin: `AI${rowNumber}`});
      // XLSX.utils.sheet_add_aoa(ws2, [[item.appletvScreenshots]], {origin: `AJ${rowNumber}`});
      
      // // check if in-app-purchase keywords are in the description
      // let tmpArrSearchResults = []
      // let tmpDesc = item.description.toLowerCase()
      // searchWord.forEach((elem,idx) => {
      //   if (tmpDesc.includes(elem)) {        
      //     tmpArrSearchResults.push(elem)
      //   }
      // })
      // XLSX.utils.sheet_add_aoa(ws2, [[tmpArrSearchResults.toString()]], {origin: `V${rowNumber}`});                                  
      
      console.log(`${item.id} ${item.title} prepared for XLSX...`)
      // rowNumber += 1

      // process.exit(1)      
    })
    XLSX.writeFile(wb, FN);                            
  }
}

main().catch(err => console.log(err))












