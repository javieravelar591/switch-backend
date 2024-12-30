const brandService = require('../services/brandService');

const getBrands = async (req, res) => {
    try {
        const brands = await brandService.getAllBrands();
        res.status(200).json(brands);
    } catch ( error ) {
        console.log("error fetching brands: ", error);
        res.status(500).json({ error: "Failed to fetch brands"});
    }
};

module.exports = {
    getBrands,
}