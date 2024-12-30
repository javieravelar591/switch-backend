const connectToDatabase = require('../config/db');

const getAllBrands = async () => {
    const db = await connectToDatabase();
    const collection = await db.collection('brand-info');
    return await collection.find().toArray();
};

module.exports = {
    getAllBrands,
};