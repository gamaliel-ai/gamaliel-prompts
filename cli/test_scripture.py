"""
Tests for the scripture module.
"""

import pytest
from unittest.mock import Mock, patch
from .scripture import BSBParser, get_bsb_parser


class TestBSBParser:
    """Test cases for BSBParser class."""
    
    def test_init(self):
        """Test parser initialization."""
        parser = BSBParser()
        assert parser.url == "https://bereanbible.com/bsb.txt"
        assert parser.verses == {}
        assert parser.chapters == {}
        assert parser._loaded is False
    
    def test_normalize_book_name(self):
        """Test book name normalization."""
        parser = BSBParser()
        
        # Test common abbreviations
        assert parser._normalize_book_name("gen") == "Genesis"
        assert parser._normalize_book_name("exo") == "Exodus"
        assert parser._normalize_book_name("mat") == "Matthew"
        assert parser._normalize_book_name("jhn") == "John"
        assert parser._normalize_book_name("rev") == "Revelation"
        
        # Test full names
        assert parser._normalize_book_name("Genesis") == "Genesis"
        assert parser._normalize_book_name("John") == "John"
        
        # Test unknown names
        assert parser._normalize_book_name("Unknown") == "Unknown"
    
    @patch('requests.get')
    def test_download_and_parse_success(self, mock_get):
        """Test successful download and parsing."""
        # Mock successful response with correct BSB format
        mock_response = Mock()
        mock_response.text = """Genesis 1:1 In the beginning God created the heavens and the earth.
Genesis 1:2 The earth was formless and void, and darkness was over the surface of the deep.
Genesis 2:1 Thus the heavens and the earth were completed, and all their hosts.
Genesis 2:2 By the seventh day God completed His work which He had done."""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Create parser with a custom cache directory to avoid conflicts
        parser = BSBParser(cache_dir="/tmp/test_cache_success")
        result = parser.download_and_parse()
        
        assert result is True
        assert parser._loaded is True
        assert "Genesis" in parser.verses
        assert 1 in parser.verses["Genesis"]
        assert 2 in parser.verses["Genesis"]
        assert 1 in parser.verses["Genesis"][1]
        assert 2 in parser.verses["Genesis"][1]
        assert "In the beginning God created" in parser.verses["Genesis"][1][1]
    
    @patch('requests.get')
    def test_download_and_parse_with_numbered_books(self, mock_get):
        """Test that books with numbers in their names are properly parsed."""
        # Mock response with numbered books that were previously failing
        mock_response = Mock()
        mock_response.text = """1 Samuel 1:1 Now there was a certain man of Ramathaim-zophim.
1 Samuel 1:2 And he had two wives.
2 Samuel 1:1 Now it came about after the death of Saul.
1 Corinthians 1:1 Paul, called as an apostle of Christ Jesus.
2 Corinthians 1:1 Paul, an apostle of Christ Jesus by the will of God.
1 Timothy 1:1 Paul, an apostle of Christ Jesus by the command of God.
2 Timothy 1:1 Paul, an apostle of Christ Jesus by the will of God.
1 Peter 1:1 Peter, an apostle of Jesus Christ.
2 Peter 1:1 Simon Peter, a servant and apostle of Jesus Christ.
1 John 1:1 What was from the beginning.
2 John 1:1 The elder to the chosen lady.
3 John 1:1 The elder to the beloved Gaius."""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Create parser with a custom cache directory to avoid conflicts
        parser = BSBParser(cache_dir="/tmp/test_cache")
        result = parser.download_and_parse()
        
        assert result is True
        assert parser._loaded is True
        
        # Check that numbered books are properly parsed
        assert "1 Samuel" in parser.verses
        assert "2 Samuel" in parser.verses
        assert "1 Corinthians" in parser.verses
        assert "2 Corinthians" in parser.verses
        assert "1 Timothy" in parser.verses
        assert "2 Timothy" in parser.verses
        assert "1 Peter" in parser.verses
        assert "2 Peter" in parser.verses
        assert "1 John" in parser.verses
        assert "2 John" in parser.verses
        assert "3 John" in parser.verses
        
        # Check that verses are properly stored
        assert 1 in parser.verses["1 Samuel"]
        assert 1 in parser.verses["1 Samuel"][1]
        assert "Now there was a certain man" in parser.verses["1 Samuel"][1][1]
        
        # Check that chapters are properly built
        assert "1 Samuel" in parser.chapters
        assert 1 in parser.chapters["1 Samuel"]
        assert "Now there was a certain man" in parser.chapters["1 Samuel"][1]
    
    @patch('requests.get')
    def test_download_and_parse_failure(self, mock_get):
        """Test download failure handling."""
        # Mock failed request
        mock_get.side_effect = Exception("Network error")
        
        # Create parser with a custom cache directory to avoid conflicts
        parser = BSBParser(cache_dir="/tmp/test_cache_failure")
        result = parser.download_and_parse()
        
        assert result is False
        assert parser._loaded is False
    
    def test_get_verse_not_loaded(self):
        """Test getting verse when data not loaded."""
        parser = BSBParser()
        
        # Mock the download_and_parse method
        with patch.object(parser, 'download_and_parse') as mock_download:
            mock_download.return_value = True
            result = parser.get_verse("Genesis", 1, 1)
            mock_download.assert_called_once()
    
    def test_get_chapter_not_loaded(self):
        """Test getting chapter when data not loaded."""
        parser = BSBParser()
        
        # Mock the download_and_parse method
        with patch.object(parser, 'download_and_parse') as mock_download:
            mock_download.return_value = True
            result = parser.get_chapter("Genesis", 1)
            mock_download.assert_called_once()
    
    def test_list_books_not_loaded(self):
        """Test listing books when data not loaded."""
        parser = BSBParser()
        
        # Mock the download_and_parse method
        with patch.object(parser, 'download_and_parse') as mock_download:
            mock_download.return_value = True
            result = parser.list_books()
            mock_download.assert_called_once()
    
    def test_search_text_not_loaded(self):
        """Test text search when data not loaded."""
        parser = BSBParser()
        
        # Mock the download_and_parse method
        with patch.object(parser, 'download_and_parse') as mock_download:
            mock_download.return_value = True
            result = parser.search_text("God")
            mock_download.assert_called_once()


class TestBSBParserIntegration:
    """Integration tests for BSBParser."""
    
    @patch('requests.get')
    def test_full_parsing_workflow(self, mock_get):
        """Test the complete parsing workflow."""
        # Mock BSB text with multiple books and chapters in correct format
        mock_response = Mock()
        mock_response.text = """Genesis 1:1 In the beginning God created the heavens and the earth.
Genesis 1:2 The earth was formless and void.
Genesis 2:1 Thus the heavens and the earth were completed.
Exodus 1:1 Now these are the names of the sons of Israel."""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Create parser with a custom cache directory to avoid conflicts
        parser = BSBParser(cache_dir="/tmp/test_cache_workflow")
        success = parser.download_and_parse()
        
        assert success is True
        assert "Genesis" in parser.verses
        assert "Exodus" in parser.verses
        assert len(parser.verses["Genesis"]) == 2
        assert len(parser.verses["Exodus"]) == 1
        
        # Test verse retrieval
        verse = parser.get_verse("Genesis", 1, 1)
        assert verse == "In the beginning God created the heavens and the earth."
        
        # Test chapter retrieval
        chapter = parser.get_chapter("Genesis", 1)
        assert "In the beginning God created" in chapter
        
        # Test book listing
        books = parser.list_books()
        assert "Genesis" in books
        assert "Exodus" in books
        
        # Test text search
        results = parser.search_text("God")
        assert len(results) > 0
        assert any("God" in result[3] for result in results)


class TestGlobalFunctions:
    """Test cases for global functions."""
    
    def test_get_bsb_parser_singleton(self):
        """Test that get_bsb_parser returns a singleton instance."""
        parser1 = get_bsb_parser()
        parser2 = get_bsb_parser()
        assert parser1 is parser2
        assert isinstance(parser1, BSBParser)


if __name__ == "__main__":
    pytest.main([__file__])
