const express = require('express');
const fs = require('fs');
const path = require('path');

const router = express.Router();

// path to static brands file
const staticBrandsFilePath = path.join(__dirname, 'data', 'brands.json');

// read static brands file
const readBrands = () => {
    const data = fs.readFileSync(staticBrandsFilePath, 'utf-8');
    return JSON.parse(data);
}

// helper func
const writeBrands = (data) => {
    fs.writeFileSync(staticBrandsFilePath, JSON.stringify(data, null, 2));
}

// fetch brands
router.get('/', (req, res) => {
    try {
        const brands = readBrands();
        res.json(brands);
    } catch (error)  {
        res.status(500).json({ error: 'Failed to fetch brands.' });
    }
});

// post a new brand
router.post('/', (req, res) => {
    try {
        const newBrand = req.body;
        const brands = readBrands;

        // assing id to brand
        newBrand.id = brands.length > 0 ? newBrand.id = brands[brands.length - 1].id + 1 : 1;
        brands.push(newBrand);
        writeBrands(brands);

        res.status(201).json(newBrand);
    } catch (error) {
        res.status(500).json({ error: 'Failed to add the brand' });
    }
})