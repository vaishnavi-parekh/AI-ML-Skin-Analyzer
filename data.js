const PROMOS={GLOW10:10,WELCOME15:15};
const A=['all'];
const P=(id,name,cat,price,e,h,skin,tones,under,concerns,desc)=>({id,name,cat,price,e,h,skin,tones,under,concerns,desc,rating:(4+((id*7)%10)/10).toFixed(1)});
const PRODUCTS=[
P(1,'Dew Drop Hyaluronic Serum','Skincare',899,'💧',200,['dry','normal','combination'],A,A,['dryness'],'Plumping hydration serum'),
P(2,'Clear Slate Niacinamide 10%','Skincare',649,'🫧',160,['oily','combination'],A,A,['oil','redness'],'Balances oil, softens pores'),
P(3,'Cloud Barrier Moisturizer','Skincare',799,'☁️',260,['dry','normal'],A,A,['dryness','redness'],'Rich ceramide cream'),
P(4,'Sunveil Gel SPF 50','Skincare',599,'☀️',45,A,A,A,[],'Weightless, no white cast'),
P(5,'Bright Eyes Caffeine Cream','Skincare',749,'👁️',280,A,A,A,['darkcircles','darkspots'],'Depuffs and brightens under-eyes'),
P(6,'Calm Cica Redness Balm','Skincare',849,'🌿',130,A,A,A,['redness'],'Soothes irritated, flushed skin'),
P(7,'Gel Cloud Cleanser','Skincare',499,'🧼',190,['oily','combination','normal'],A,A,['oil'],'Gentle daily foaming gel'),
P(8,'Vitamin C Glow Drops','Skincare',999,'🍊',30,A,A,A,['darkspots','pigmentation'],'Brightening antioxidant serum'),
P(9,'Porcelain Veil Foundation','Makeup',1199,'🤍',340,A,['fair','light'],['cool','neutral'],[],'Skin-like medium coverage'),
P(10,'Warm Sand Foundation','Makeup',1199,'🟡',35,A,['medium','tan'],['warm','neutral'],[],'Golden, natural finish'),
P(11,'Deep Cocoa Foundation','Makeup',1199,'🤎',20,A,['tan','deep'],['warm','neutral'],[],'Rich shade range, no ashiness'),
P(12,'Velvet Rose Lip Tint','Makeup',549,'💋',345,A,['fair','light','medium'],A,[],'Sheer petal-pink color'),
P(13,'Berry Wine Lipstick','Makeup',649,'💄',330,A,['medium','tan','deep'],A,[],'Bold, creamy matte'),
P(14,'Coral Bloom Blush','Makeup',699,'🌸',10,A,A,['warm','neutral'],[],'Sun-warmed cheek color'),
P(15,'Lilac Mist Blush','Makeup',699,'🪻',290,A,A,['cool','neutral'],[],'Cool, cloudy flush'),
P(16,'Argan Repair Hair Oil','Haircare',799,'✨',40,A,A,A,[],'Shine and frizz control'),
P(17,'Midnight Bloom Eau de Parfum','Fragrance',1799,'🌙',270,A,A,A,[],'Jasmine, amber, soft musk')];
