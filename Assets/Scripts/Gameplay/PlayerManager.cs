using UnityEngine;
using System.Collections.Generic;
using LOTRCardGame.Data;

namespace LOTRCardGame.Gameplay
{
    /// <summary>
    /// Represents one player's entire game state: resources, card zones, hero.
    /// Mirrors the Python engine/player.py PlayerState class.
    /// </summary>
    public class PlayerManager : MonoBehaviour
    {
        [Header("Identity")]
        public string playerName;
        public Faction faction;
        public bool isFreePeoples;

        [Header("Resources")]
        public int influence = 30;
        public int willpowerMax = 1;
        public int willpowerPool;

        [Header("Card Zones")]
        public List<CardData> deck = new List<CardData>();
        public List<CardData> hand = new List<CardData>();
        public List<CardData> discard = new List<CardData>();

        [Header("Hero")]
        public BoardAlly hero;
        public bool heroInPlay = true;

        [Header("Status")]
        public bool leaderless;
        public int fatigueCounter;
        public int turnNumber;

        // --- Computed Properties ---

        public int EffectiveWillpowerMax => leaderless
            ? Mathf.Max(1, willpowerMax - 2)
            : willpowerMax;

        public int HandSize => hand.Count;

        public int DeckSize => deck.Count;

        public bool IsDefeated() => influence <= 0;

        // --- Card Operations ---

        /// <summary>
        /// Draw a card from deck. Returns null if deck empty (fatigue).
        /// </summary>
        public CardData DrawCard()
        {
            if (deck.Count == 0)
            {
                fatigueCounter++;
                influence -= fatigueCounter;
                return null;
            }
            int lastIdx = deck.Count - 1;
            CardData card = deck[lastIdx];
            deck.RemoveAt(lastIdx);
            hand.Add(card);
            return card;
        }

        /// <summary>
        /// Draw n cards.
        /// </summary>
        public List<CardData> DrawCards(int n)
        {
            var drawn = new List<CardData>();
            for (int i = 0; i < n; i++)
            {
                CardData c = DrawCard();
                if (c != null)
                    drawn.Add(c);
                else
                    break;
            }
            return drawn;
        }

        /// <summary>
        /// Remove a card from hand to play it. Returns true if found.
        /// </summary>
        public bool PlayCard(CardData card)
        {
            for (int i = 0; i < hand.Count; i++)
            {
                if (hand[i] == card)
                {
                    hand.RemoveAt(i);
                    return true;
                }
            }
            return false;
        }

        /// <summary>
        /// Discard a specific card from hand.
        /// </summary>
        public bool DiscardCard(CardData card)
        {
            for (int i = 0; i < hand.Count; i++)
            {
                if (hand[i] == card)
                {
                    hand.RemoveAt(i);
                    discard.Add(card);
                    return true;
                }
            }
            return false;
        }

        // --- Resources ---

        /// <summary>
        /// Spend willpower. Returns true if successful.
        /// </summary>
        public bool SpendWillpower(int amount)
        {
            if (willpowerPool >= amount)
            {
                willpowerPool -= amount;
                return true;
            }
            return false;
        }

        /// <summary>
        /// Add temporary willpower (can exceed cap).
        /// </summary>
        public void AddWillpower(int amount)
        {
            willpowerPool += amount;
        }

        /// <summary>
        /// Deal direct damage to influence.
        /// </summary>
        public void DealInfluenceDamage(int amount)
        {
            influence = Mathf.Max(0, influence - amount);
        }

        // --- Utility ---

        /// <summary>
        /// Shuffle the deck (Fisher-Yates).
        /// </summary>
        public void ShuffleDeck()
        {
            for (int i = deck.Count - 1; i > 0; i--)
            {
                int j = Random.Range(0, i + 1);
                (deck[i], deck[j]) = (deck[j], deck[i]);
            }
        }
    }
}
