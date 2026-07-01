using UnityEngine;
using LOTRCardGame.Data;

namespace LOTRCardGame.Gameplay
{
    /// <summary>
    /// Factory methods for token creatures (Orc, Goblin, Rider, Uruk-hai).
    /// Tokens are lightweight CardData instances created at runtime.
    /// Mirrors Python engine/effects.py token factory functions.
    /// </summary>
    public static class TokenFactory
    {
        public static CardData CreateOrcToken()
        {
            return ScriptableObject.CreateInstance<CardData>();
            // NOTE: ScriptableObject.CreateInstance bypasses the asset database.
            // For production, tokens should be pre-made .asset files or created
            // via a ScriptableObject pool. This works for prototype use.
        }

        public static void ConfigureOrcToken(CardData token)
        {
            token.cardName = "Orc Token";
            token.faction = Faction.Mordor;
            token.cardType = CardType.Ally;
            token.cost = 0;
            token.power = 1;
            token.toughness = 1;
            token.creatureTypes = new System.Collections.Generic.List<string> { "Orc" };
            token.rulesText = "Token creature.";
        }

        public static void ConfigureRiderToken(CardData token)
        {
            token.cardName = "Rider Token";
            token.faction = Faction.Rohan;
            token.cardType = CardType.Ally;
            token.cost = 0;
            token.power = 2;
            token.toughness = 1;
            token.creatureTypes = new System.Collections.Generic.List<string> { "Man", "Rider" };
            token.keywords = new System.Collections.Generic.List<string> { "Charge" };
            token.rulesText = "Charge. Token creature.";
        }

        public static void ConfigureGoblinToken(CardData token)
        {
            token.cardName = "Goblin Token";
            token.faction = Faction.Moria;
            token.cardType = CardType.Ally;
            token.cost = 0;
            token.power = 1;
            token.toughness = 1;
            token.creatureTypes = new System.Collections.Generic.List<string> { "Goblin" };
            token.rulesText = "Token creature.";
        }

        public static void ConfigureUrukHaiToken(CardData token, int power = 3, int toughness = 3)
        {
            token.cardName = "Uruk-hai Token";
            token.faction = Faction.Isengard;
            token.cardType = CardType.Ally;
            token.cost = 0;
            token.power = power;
            token.toughness = toughness;
            token.creatureTypes = new System.Collections.Generic.List<string> { "Uruk-hai" };
            token.rulesText = "Token creature.";
        }
    }
}
