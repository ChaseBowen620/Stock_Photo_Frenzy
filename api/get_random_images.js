export default async function handler(req, res) {
  try {
    const { query = 'random', numImages = 10, titleLength = 100 } = req.query;
    console.log('Received request for images:', { query, numImages, titleLength });
    
    // For now, let's use placeholder images
    const images = Array.from({ length: parseInt(numImages) }, (_, i) => ({
      url: `https://picsum.photos/800/${600 + i}`,
      title: `Sample Image ${i + 1} with some descriptive text that might be useful for guessing`,
      truncatedTitle: `Sample Image ${i + 1}`
    }));

    console.log(`Sending ${images.length} images`);
    res.status(200).json(images);
  } catch (error) {
    console.error('Error fetching images:', error);
    res.status(500).json({ error: 'Failed to fetch images' });
  }
} 