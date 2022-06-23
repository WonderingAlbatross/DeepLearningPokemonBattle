from poke_env.environment.pokemon_type import PokemonType


antitypeberry = ("occaberry","passhoberry","wacanberry","rindoberry","rindoberry","yacheberry","chopleberry","kebiaberry","shucaberry","cobaberry","payapaberry","tangaberry","chartiberry","kasibberry","habanberry","colburberry","babiriberry","chilanberry","roseliberry")
giantberry = ("aguavberry","figyberry","iapapaberry","magoberry","wikiberry")


# A: ability I: item M:Move T: type S: IV & nature (fastatt,fastspa,slowstt,slowspa,bulkatt,bulkspa,stall)
def A_I_covariance(ability,item):
	c = 0
	if ability == "unburden" and _is_consumable(item):
		c = 1
	if ability in ("guts","marvelscale","flareboost") and item == "flameorb":
		c = 1
	if ability in ("poisonheal","toxicboost") and item == "toxicorb":
		c = 1
		
	return c


def M_I_covariance(move,item):
	c = 0
	if move.entry["category"] == "Status":
		if item == "assaultvest":
			c = -1
		if item in ("choiceband","choicespecs","choicescarf"):
			c = -0.9

		
	return c


def M_A_covariance(a,b):
	c = 0
	return c


def M_M_covariance(a,b):
	c = 0
	return c


def M_S_covariance(a,b):
	c = 0
	return c

def T_I_covariance(type:PokemonType,b):
	t = type.name
	c = 0
	if b == "leftover" and t == "POISON":
		c = -1
	if b == "blacksludge" and t != "POISON":
		c = -1	
	return c	

def T_M_covariance(a,b):
	return 0

def _is_consumable(a):
	return 0


#guess hp from leechseed, 50damage

