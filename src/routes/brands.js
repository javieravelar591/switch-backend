const express = require('express');
const router = express.Router();
const brandController = require('../controllers/brandController');


// fetch brands
router.get('/brands', brandController.getBrands);

// post a new brand
// router.post('/', (req, res) => {
//     try {
//         const newBrand = req.body;
//         const brands = readBrands;

//         // assing id to brand
//         newBrand.id = brands.length > 0 ? newBrand.id = brands[brands.length - 1].id + 1 : 1;
//         brands.push(newBrand);
//         writeBrands(brands);

//         res.status(201).json(newBrand);
//     } catch (error) {
//         res.status(500).json({ error: 'Failed to add the brand' });
//     }
// });

module.exports = router;