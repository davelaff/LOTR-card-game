using UnityEngine;
using System.Collections.Generic;
using System.Linq;

namespace LOTRCardGame.Data
{
    /// <summary>
    /// Static runtime card database. Loads all CardData ScriptableObjects from Resources.
    /// Provides indexed lookups by name, faction, and card type.
    /// Call CardLibrary.Initialize() once before use (typically in GameManager.Setup).
    /// </summary>
    public static class CardLibrary
    {
        private static bool initialized;
        private static Dictionary<string, CardData> byName;
        private static Dictionary<Faction, List<CardData>> byFaction;
        private static Dictionary<Faction, CardData> heroByFaction;
        private static Dictionary<Faction, List<CardData>> nonHeroByFaction;

        /// <summary>
        /// Load all CardData assets from Resources/Cards/. Must be called before any lookups.
        /// </summary>
        public static void Initialize()
        {
            if (initialized) return;

            byName = new Dictionary<string, CardData>();
            byFaction = new Dictionary<Faction, List<CardData>>();
            heroByFaction = new Dictionary<Faction, CardData>();
            nonHeroByFaction = new Dictionary<Faction, List<CardData>>();

            CardData[] allCards = Resources.LoadAll<CardData>("Cards");
            Debug.Log($"[CardLibrary] Loaded {allCards.Length} cards from Resources/Cards/");

            foreach (CardData card in allCards)
            {
                if (card == null) continue;

                // Index by name
                byName[card.cardName] = card;

                // Index by faction
                if (!byFaction.ContainsKey(card.faction))
                    byFaction[card.faction] = new List<CardData>();
                byFaction[card.faction].Add(card);

                // Separate heroes from non-heroes
                if (card.cardType == CardType.Hero)
                {
                    if (heroByFaction.ContainsKey(card.faction))
                        Debug.LogWarning($"[CardLibrary] Multiple heroes for {card.faction}: " +
                            $"'{heroByFaction[card.faction].cardName}' and '{card.cardName}'. Using first.");
                    else
                        heroByFaction[card.faction] = card;
                }
                else
                {
                    if (!nonHeroByFaction.ContainsKey(card.faction))
                        nonHeroByFaction[card.faction] = new List<CardData>();
                    nonHeroByFaction[card.faction].Add(card);
                }
            }

            initialized = true;
            Debug.Log($"[CardLibrary] Indexed {byName.Count} cards, {heroByFaction.Count} heroes, " +
                $"{byFaction.Count} factions.");
        }

        /// <summary>
        /// Look up a card by exact name.
        /// </summary>
        public static CardData GetCard(string name)
        {
            if (!initialized) Initialize();
            byName.TryGetValue(name, out CardData card);
            return card;
        }

        /// <summary>
        /// Get all cards belonging to a faction.
        /// </summary>
        public static List<CardData> GetFactionCards(Faction faction)
        {
            if (!initialized) Initialize();
            byFaction.TryGetValue(faction, out List<CardData> cards);
            return cards ?? new List<CardData>();
        }

        /// <summary>
        /// Get the hero card for a faction, or null.
        /// </summary>
        public static CardData GetHero(Faction faction)
        {
            if (!initialized) Initialize();
            heroByFaction.TryGetValue(faction, out CardData hero);
            return hero;
        }

        /// <summary>
        /// Get all non-hero cards for a faction (deck-building pool).
        /// </summary>
        public static List<CardData> GetDeckCards(Faction faction)
        {
            if (!initialized) Initialize();
            nonHeroByFaction.TryGetValue(faction, out List<CardData> cards);
            return cards ?? new List<CardData>();
        }
    }
}
