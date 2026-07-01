using UnityEngine;
using System.Collections.Generic;

namespace LOTRCardGame.Data
{
    [CreateAssetMenu(fileName = "CardData", menuName = "LOTR Card Game/Card Data")]
    public class CardData : ScriptableObject
    {
        [Header("Identity")]
        public string cardName;
        public Faction faction;
        public CardType cardType;
        public Rarity rarity;

        [Header("Stats")]
        public int cost;
        public int power;
        public int toughness;
        public int defense;

        [Header("Text")]
        [TextArea(2, 6)]
        public string rulesText;
        [TextArea(1, 3)]
        public string flavorText;

        [Header("Traits")]
        public List<string> creatureTypes = new List<string>();
        public List<string> keywords = new List<string>();

        [Header("Art")]
        public Sprite cardArt;

        /// <summary>
        /// Full display name for debugging and UI.
        /// </summary>
        public string DisplayName => $"{cardName} ({faction} {cardType})";
    }
}
